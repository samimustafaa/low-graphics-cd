// Catch recognized sky shaders created through resource/native device references.
// Cache is bounded, render-thread owned, and never classifies ground by draw state.
static void clearSkyBindings(DeviceContext* c) {
    for(auto& e:c->skyBindings) {
        if(e.replacement)IDirect3DPixelShader9_Release(e.replacement);
        if(e.source)IDirect3DPixelShader9_Release(e.source);
        e={};
    }
}
static IDirect3DPixelShader9* skyForBinding(DeviceContext* c,IDirect3DPixelShader9* shader) {
    uintptr_t key=(uintptr_t)shader;
    auto& entry=c->skyBindings[((key>>4)^(key>>12))&255];
    if(entry.source==shader)return entry.replacement?entry.replacement:shader;
    if(entry.replacement)IDirect3DPixelShader9_Release(entry.replacement);
    if(entry.source)IDirect3DPixelShader9_Release(entry.source);
    entry={shader,nullptr};IDirect3DPixelShader9_AddRef(shader);
    ++c->skyBindReads;
    UINT bytes=0;
    if(FAILED(IDirect3DPixelShader9_GetFunction(shader,nullptr,&bytes)) || bytes<8 || bytes>1024*1024 || bytes%4)return shader;
    UINT capacity=bytes;auto code=(DWORD*)HeapAlloc(GetProcessHeap(),0,capacity);
    if(!code)return shader;
    SkyMetadata m={};
    size_t opaqueWords=0;
    if(SUCCEEDED(IDirect3DPixelShader9_GetFunction(shader,code,&bytes)) && bytes<=capacity && bytes%4==0 &&
       ((c->config.opaqueStructures && (opaqueWords=makeOpaqueStructure((const uint32_t*)code,bytes/4,nullptr))) ||
        (c->config.neutralSky && findSkyMetadata((const uint32_t*)code,bytes/4,&m)))) {
        ++c->skyBindMatches;
        size_t words=opaqueWords?opaqueWords:graySkyWordCount(m);
        auto solid=(DWORD*)HeapAlloc(GetProcessHeap(),0,words*4);
        if(solid) {
            if(opaqueWords)makeOpaqueStructure((const uint32_t*)code,bytes/4,(uint32_t*)solid);
            else makeGraySky(m,(uint32_t*)solid,c->config.blackSky);
            // Creation-time replacements already have the correct program.
            if(words*4!=bytes || memcmp(code,solid,bytes)!=0) {
                IDirect3DPixelShader9* replacement=nullptr;
                HRESULT hr=c->original->CreatePixelShader(c->real,solid,&replacement);
                if(SUCCEEDED(hr) && replacement) {
                    entry.replacement=replacement;
                    logLine(opaqueWords?"Opaque structure replacement cached; original RGB retained.":c->config.blackSky?"Black SKY replacement cached at shader bind.":"Gray SKY replacement cached at shader bind.");
                } else logLine("Sky bind replacement rejected; original retained.");
            }
            HeapFree(GetProcessHeap(),0,solid);
        }
    } else ++c->skyBindMisses;
    HeapFree(GetProcessHeap(),0,code);
    return entry.replacement?entry.replacement:shader;
}
static HRESULT STDMETHODCALLTYPE setPixelShader(IDirect3DDevice9* d,IDirect3DPixelShader9* shader) {
    auto c=ctx(d);Hold<DeviceContext> hold(c);CallGuard entry;
    if(!entry.outer || !shader || !c->config.enabled || !(c->config.neutralSky || c->config.opaqueStructures) || c->config.bypass ||
       c->blocked || c->recording || !ownsThread(c))return c->original->SetPixelShader(c->real,shader);
    auto mapped=skyForBinding(c,shader);
    HRESULT hr=c->original->SetPixelShader(c->real,mapped);
    if(FAILED(hr) && mapped!=shader) {
        hr=c->original->SetPixelShader(c->real,shader);
        uintptr_t key=(uintptr_t)shader;auto& e=c->skyBindings[((key>>4)^(key>>12))&255];
        if(e.source==shader && e.replacement){IDirect3DPixelShader9_Release(e.replacement);e.replacement=nullptr;}
        logLine("Sky bind failed; original shader restored.");
    }
    return hr;
}
static HRESULT STDMETHODCALLTYPE getPixelShader(IDirect3DDevice9* d,IDirect3DPixelShader9** out) {
    auto c=ctx(d);Hold<DeviceContext> hold(c);CallGuard entry;
    HRESULT hr=c->original->GetPixelShader(c->real,out);
    if(entry.outer && c->config.enabled && (c->config.neutralSky || c->config.opaqueStructures) && !c->config.bypass && SUCCEEDED(hr) && out && *out && ownsThread(c)) {
        for(const auto& e:c->skyBindings)if(e.replacement==*out) {
            IDirect3DPixelShader9_AddRef(e.source);IDirect3DPixelShader9_Release(*out);*out=e.source;break;
        }
    }
    return hr;
}
