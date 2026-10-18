#define TEXTURELAB_NATIVE_TEST
#include "../native/texture_lab.cpp"
#include <assert.h>
#include <vector>
#include <random>
struct Shader {const IDirect3DPixelShader9Vtbl*lpVtbl;ULONG refs;std::vector<DWORD> code;bool failRead;};
static IDirect3DPixelShader9Vtbl shaderTable;
static IDirect3DDevice9Vtbl deviceTable;
static Shader original, replacement;
static bool rejectReplacement=false;
static unsigned creates=0;
static ULONG STDMETHODCALLTYPE shaderRelease(IDirect3DPixelShader9* s){return --((Shader*)s)->refs;}
static HRESULT STDMETHODCALLTYPE shaderRead(IDirect3DPixelShader9* s,void* out,UINT* bytes){
    auto f=(Shader*)s;if(f->failRead)return D3DERR_INVALIDCALL;
    if(out){if(*bytes<f->code.size()*4)return D3DERR_INVALIDCALL;memcpy(out,f->code.data(),f->code.size()*4);}
    *bytes=(UINT)f->code.size()*4;return S_OK;
}
static HRESULT STDMETHODCALLTYPE shaderCreate(IDirect3DDevice9*,const DWORD* code,IDirect3DPixelShader9** out){
    ++creates;
    if(code==original.code.data()){original.refs=1;*out=(IDirect3DPixelShader9*)&original;return S_OK;}
    if(rejectReplacement){*out=nullptr;return D3DERR_INVALIDCALL;}
    SkyMetadata m={};assert(findSkyMetadata((const uint32_t*)original.code.data(),original.code.size(),&m));
    replacement.code.assign(code,code+graySkyWordCount(m));replacement.refs=1;
    assert(replacement.code[0]==original.code[0]);
    assert(replacement.code.back()==0x0000ffff);
    assert(memcmp(code+1,m.comment,m.words*4)==0); // Reflection comment preserved byte-for-byte.
    *out=(IDirect3DPixelShader9*)&replacement;return S_OK;
}
static std::vector<DWORD> fixture(bool sky=true,DWORD version=0xffff0200){
    const char names[]="\0skycolormid\0skycolorlow\0u_bg_color\0";
    const char terrain[]="\0sky_color\0FogInfo\0texture_sampler\0";
    size_t bytes=sky?sizeof(names):sizeof(terrain);size_t words=1+(bytes+3)/4;
    std::vector<DWORD> code(3+words,0);code[0]=version;code[1]=0xfffe|((DWORD)words<<16);code[2]=0x42415443;
    memcpy(code.data()+3,sky?names:terrain,bytes);code.back()=0xffff;return code;
}
int main(){
    reentryTLS=TlsAlloc();shaderTable.Release=shaderRelease;shaderTable.GetFunction=shaderRead;
    original.lpVtbl=replacement.lpVtbl=&shaderTable;deviceTable.CreatePixelShader=shaderCreate;
    IDirect3DDevice9 real={&deviceTable};DeviceContext c={};c.real=&real;c.original=&deviceTable;
    c.config={true,15,32,false,true,true};
    auto wrapper=(IDirect3DDevice9*)&c;
    for(DWORD version:{0xffff0200u,0xffff0300u}){
        original.code=fixture(true,version);IDirect3DPixelShader9* result=nullptr;
        assert(SUCCEEDED(createPixelShader(wrapper,original.code.data(),&result)));
        assert(result==(IDirect3DPixelShader9*)&replacement && original.refs==0);
        assert(IDirect3DPixelShader9_Release(result)==0);
    }
    original.code=fixture(false);IDirect3DPixelShader9* result=nullptr;
    unsigned before=creates;
    assert(SUCCEEDED(createPixelShader(wrapper,original.code.data(),&result)));
    assert(result==(IDirect3DPixelShader9*)&original && creates==before+1);IDirect3DPixelShader9_Release(result);
    original.code=fixture();rejectReplacement=true;
    assert(SUCCEEDED(createPixelShader(wrapper,original.code.data(),&result)) && result==(IDirect3DPixelShader9*)&original);
    assert(original.refs==1);IDirect3DPixelShader9_Release(result);rejectReplacement=false;
    for(int mode=0;mode<3;++mode){
        c.config.enabled=mode!=0;c.config.neutralSky=mode!=1;original.failRead=mode==2;
        before=creates;assert(SUCCEEDED(createPixelShader(wrapper,original.code.data(),&result)));
        assert(creates==before+1 && result==(IDirect3DPixelShader9*)&original);IDirect3DPixelShader9_Release(result);
    }
    SkyMetadata m={};auto malformed=fixture();malformed[1]=0x7ffffffe;
    assert(!findSkyMetadata((const uint32_t*)malformed.data(),malformed.size(),&m));
    auto good=fixture();
    for(size_t n=0;n<good.size();++n){ // Every truncated prefix is safe to parse.
        findSkyMetadata((const uint32_t*)good.data(),n,&m);
    }
    std::mt19937 random(0x504f5441);
    for(int k=0;k<10000;++k){std::vector<uint32_t> fuzz(random()%128);for(auto& w:fuzz)w=random();if(!fuzz.empty())fuzz[0]=0xffff0300;findSkyMetadata(fuzz.data(),fuzz.size(),&m);}
#ifdef TEXTURELAB_HOST_TEST
    assert(contextAllocations==0);
#endif
    puts("PASS: targeted sky recognition, shader-model preservation, CTAB retention, replacement fallback, off switch, malformed/truncated metadata, 10,000 parser fuzz cases");
}
