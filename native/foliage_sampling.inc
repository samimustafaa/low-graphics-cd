// Protect coverage at the actual draw boundary. Shader/alpha state may have
// changed after SetTexture, including via a native device or state block.
// Cache immutable shader analysis; never lock/read back textures or edit pixels.
static bool needsOriginalCoverage(const DWORD* code,size_t words) {
    if(!code || words<2 || (code[0]!=0xffff0200u && code[0]!=0xffff0300u))return true;
    for(size_t i=1;i<words;) {
        DWORD token=code[i],op=token&0xffff;
        if(op==0xffff)return i!=words-1;
        size_t n=op==0xfffe?((token>>16)&0x7fff):((token>>24)&15);
        if(n>words-i-1)return true;
        if(op==65)return true; // TEXKILL / HLSL clip: alpha-cutout coverage.
        i+=n+1;
    }
    return true; // Unknown/truncated programs keep original sampling.
}
static void clearCutoutBindings(DeviceContext* c) {
    for(auto& e:c->cutoutBindings){if(e.source)IDirect3DPixelShader9_Release(e.source);e={};}
}
static bool cutoutProgram(DeviceContext* c,IDirect3DPixelShader9* shader) {
    if(!shader)return false; // Fixed-function alpha states are checked separately.
    uintptr_t key=(uintptr_t)shader;
    auto& e=c->cutoutBindings[((key>>4)^(key>>12))&255];
    if(e.source==shader)return e.protect;
    if(e.source)IDirect3DPixelShader9_Release(e.source);
    e={shader,true};IDirect3DPixelShader9_AddRef(shader);
    UINT bytes=0;
    if(FAILED(IDirect3DPixelShader9_GetFunction(shader,nullptr,&bytes)) || bytes<8 || bytes>1024*1024 || bytes%4)return true;
    UINT capacity=bytes;auto code=(DWORD*)HeapAlloc(GetProcessHeap(),0,capacity);
    if(!code)return true;
    if(SUCCEEDED(IDirect3DPixelShader9_GetFunction(shader,code,&bytes)) && bytes<=capacity && bytes%4==0)
        e.protect=needsOriginalCoverage(code,bytes/4);
    HeapFree(GetProcessHeap(),0,code);return e.protect;
}
static void prepareTextureDraw(DeviceContext* c) {
    if(!c->config.enabled || !c->config.bias || c->config.bypass || c->blocked || c->recording || !ownsThread(c))return;
    bool active=false;
    for(const auto& s:c->samplers)if(s.baseEligible || s.applied || s.filterApplied || s.mipApplied){active=true;break;}
    if(!active)return;
    // Read actual state, not the last wrapper call: resource GetDevice and state
    // blocks can bind shaders without passing through SetPixelShader here.
    DWORD test=0,blend=0;IDirect3DPixelShader9* shader=nullptr;
    bool protect=!c->original->GetRenderState || !c->original->GetPixelShader;
    if(!protect) {
        HRESULT a=c->original->GetRenderState(c->real,D3DRS_ALPHATESTENABLE,&test);
        HRESULT b=c->original->GetRenderState(c->real,D3DRS_ALPHABLENDENABLE,&blend);
        HRESULT p=c->original->GetPixelShader(c->real,&shader);
        protect=FAILED(a) || FAILED(b) || FAILED(p) || test || blend || cutoutProgram(c,shader);
    }
    if(shader)IDirect3DPixelShader9_Release(shader);
    c->cutoutDraw=protect;
    for(DWORD slot=0;slot<16 && !c->blocked;++slot) {
        auto& s=c->samplers[slot];s.eligible=s.baseEligible && !protect;
        DWORD value=desired(c,slot,s.eligible);
        if((s.eligible || s.applied) && (!s.applied || s.appliedValue!=value))apply(c,slot,value);
        applyFilter(c,slot,s.eligible);applyMip(c,slot,s.eligible);
    }
}
static HRESULT STDMETHODCALLTYPE drawPrimitive(IDirect3DDevice9* d,D3DPRIMITIVETYPE type,UINT start,UINT count) {
    auto c=ctx(d);Hold<DeviceContext> hold(c);CallGuard entry;if(entry.outer)prepareTextureDraw(c);
    return c->original->DrawPrimitive(c->real,type,start,count);
}
static HRESULT STDMETHODCALLTYPE drawIndexedPrimitive(IDirect3DDevice9* d,D3DPRIMITIVETYPE type,INT base,UINT first,UINT vertices,UINT start,UINT count) {
    auto c=ctx(d);Hold<DeviceContext> hold(c);CallGuard entry;if(entry.outer)prepareTextureDraw(c);
    return c->original->DrawIndexedPrimitive(c->real,type,base,first,vertices,start,count);
}
static HRESULT STDMETHODCALLTYPE drawPrimitiveUP(IDirect3DDevice9* d,D3DPRIMITIVETYPE type,UINT count,const void* data,UINT stride) {
    auto c=ctx(d);Hold<DeviceContext> hold(c);CallGuard entry;if(entry.outer)prepareTextureDraw(c);
    return c->original->DrawPrimitiveUP(c->real,type,count,data,stride);
}
static HRESULT STDMETHODCALLTYPE drawIndexedPrimitiveUP(IDirect3DDevice9* d,D3DPRIMITIVETYPE type,UINT first,UINT vertices,UINT count,const void* indices,D3DFORMAT format,const void* data,UINT stride) {
    auto c=ctx(d);Hold<DeviceContext> hold(c);CallGuard entry;if(entry.outer)prepareTextureDraw(c);
    return c->original->DrawIndexedPrimitiveUP(c->real,type,first,vertices,count,indices,format,data,stride);
}
