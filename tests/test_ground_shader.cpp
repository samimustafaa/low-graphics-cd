#define TEXTURELAB_NATIVE_TEST
#include "../native/texture_lab.cpp"
#include <assert.h>
#include <vector>
#include <random>
const char grassNames[]="\0WindInfo\0u_visible_dist\0char_pos\0u_wvp\0";
const char groundNames[]="\0safe_range_color\0char_pos\0sky_color\0weather_intensity\0sam_other0\0";
static std::vector<DWORD> fixture(DWORD version,const char* names,size_t bytes) {
    size_t count=1+(bytes+3)/4;
    std::vector<DWORD> code(2+count,0);code[0]=version;code[1]=0xfffe|((DWORD)count<<16);code[2]=0x42415443;
    memcpy(code.data()+3,names,bytes);
    if(version==0xfffe0300u){const DWORD decl[]={0x0200001f,0x80000000,0xe00f0002,0x0200001f,0x80000005,0xe0030005};code.insert(code.end(),decl,decl+6);}
    code.push_back(0xffff);return code;
}
struct Vertex {const IDirect3DVertexShader9Vtbl* lpVtbl;ULONG refs;std::vector<DWORD> code;bool failRead;};
struct Pixel {const IDirect3DPixelShader9Vtbl* lpVtbl;ULONG refs;std::vector<DWORD> code;};
static Vertex original,replacement;static Pixel originalPixel,replacementPixel;
static IDirect3DVertexShader9Vtbl vertexTable;static IDirect3DPixelShader9Vtbl pixelTable;static IDirect3DDevice9Vtbl deviceTable;
static bool reject=false;static unsigned creates=0;
static ULONG STDMETHODCALLTYPE vertexRelease(IDirect3DVertexShader9* p){return --((Vertex*)p)->refs;}
static ULONG STDMETHODCALLTYPE pixelRelease(IDirect3DPixelShader9* p){return --((Pixel*)p)->refs;}
static HRESULT STDMETHODCALLTYPE vertexRead(IDirect3DVertexShader9* p,void* out,UINT* bytes) {
    auto s=(Vertex*)p;if(s->failRead)return D3DERR_INVALIDCALL;
    if(out){if(*bytes<s->code.size()*4)return D3DERR_INVALIDCALL;memcpy(out,s->code.data(),s->code.size()*4);}
    *bytes=(UINT)s->code.size()*4;return S_OK;
}
static HRESULT STDMETHODCALLTYPE pixelRead(IDirect3DPixelShader9* p,void* out,UINT* bytes) {
    auto s=(Pixel*)p;if(out){if(*bytes<s->code.size()*4)return D3DERR_INVALIDCALL;memcpy(out,s->code.data(),s->code.size()*4);}
    *bytes=(UINT)s->code.size()*4;return S_OK;
}
static HRESULT STDMETHODCALLTYPE vertexCreate(IDirect3DDevice9*,const DWORD* code,IDirect3DVertexShader9** out) {
    ++creates;if(code==original.code.data()){original.refs=1;*out=(IDirect3DVertexShader9*)&original;return S_OK;}
    if(reject){*out=nullptr;return D3DERR_INVALIDCALL;}
    SkyMetadata m={};assert(groundKind((const uint32_t*)original.code.data(),original.code.size(),&m)==GroundShader::Grass);
    size_t words=makeNoGrass((const uint32_t*)original.code.data(),original.code.size(),m,nullptr);assert(words);
    replacement.code.assign(code,code+words);replacement.refs=1;*out=(IDirect3DVertexShader9*)&replacement;return S_OK;
}
static HRESULT STDMETHODCALLTYPE pixelCreate(IDirect3DDevice9*,const DWORD* code,IDirect3DPixelShader9** out) {
    if(code==originalPixel.code.data()){originalPixel.refs=1;*out=(IDirect3DPixelShader9*)&originalPixel;return S_OK;}
    if(reject){*out=nullptr;return D3DERR_INVALIDCALL;}
    SkyMetadata m={};assert(groundKind((const uint32_t*)originalPixel.code.data(),originalPixel.code.size(),&m)==GroundShader::Terrain);
    replacementPixel.code.assign(code,code+graySkyWordCount(m));replacementPixel.refs=1;*out=(IDirect3DPixelShader9*)&replacementPixel;return S_OK;
}
int main() {
    reentryTLS=TlsAlloc();vertexTable.Release=vertexRelease;vertexTable.GetFunction=vertexRead;pixelTable.Release=pixelRelease;pixelTable.GetFunction=pixelRead;
    original.lpVtbl=replacement.lpVtbl=&vertexTable;originalPixel.lpVtbl=replacementPixel.lpVtbl=&pixelTable;
    deviceTable.CreateVertexShader=vertexCreate;deviceTable.CreatePixelShader=pixelCreate;
    IDirect3DDevice9 real={&deviceTable};DeviceContext c={};c.real=&real;c.original=&deviceTable;c.config.enabled=true;c.config.flatGround=true;auto wrapper=(IDirect3DDevice9*)&c;
    for(DWORD version:{0xfffe0200u,0xfffe0300u}) {
        original.code=fixture(version,grassNames,sizeof(grassNames));IDirect3DVertexShader9* result=nullptr;
        assert(SUCCEEDED(createVertexShader(wrapper,original.code.data(),&result)) && result==(IDirect3DVertexShader9*)&replacement && original.refs==0);
        SkyMetadata m={};assert(groundKind((const uint32_t*)replacement.code.data(),replacement.code.size(),&m)==GroundShader::Grass);
        assert(replacement.code[0]==version && replacement.code.back()==0xffff);
        assert(memcmp(replacement.code.data()+1,original.code.data()+1,m.words*4)==0);
        size_t start=1+m.words+(version==0xfffe0300u?6:0);
        assert(replacement.code[start+4]==0xbf800000u && replacement.code[start+5]==0x3f800000u);
        for(size_t i=start+6;i+1<replacement.code.size();i+=3){assert(replacement.code[i]==0x02000001u);assert(replacement.code[i+2]==0xa0e40000u);}
        IDirect3DVertexShader9_Release(result);
        for(int mode=0;mode<5;++mode) {
            c.config.enabled=mode!=0;c.config.bypass=mode==1;original.failRead=mode==2;reject=mode==3;c.config.flatGround=mode!=4;
            assert(SUCCEEDED(createVertexShader(wrapper,original.code.data(),&result)) && result==(IDirect3DVertexShader9*)&original && original.refs==1);IDirect3DVertexShader9_Release(result);
        }
        c.config.enabled=true;c.config.bypass=false;original.failRead=false;reject=false;c.config.flatGround=true;
    }
    for(bool dark:{false,true}) for(DWORD version:{0xffff0200u,0xffff0300u}) {
        c.config.neutralSky=dark;
        originalPixel.code=fixture(version,groundNames,sizeof(groundNames));IDirect3DPixelShader9* result=nullptr;
        assert(SUCCEEDED(createPixelShader(wrapper,originalPixel.code.data(),&result)) && result==(IDirect3DPixelShader9*)&replacementPixel);
        size_t start=replacementPixel.code.size()-10;
        assert(replacementPixel.code[start+2]==(dark?0x3e8f5c29u:0x3f3851ecu));
        assert(replacementPixel.code[start+3]==(dark?0x3eae147bu:0x3f3d70a4u));
        assert(replacementPixel.code[start+4]==(dark?0x3e4ccccdu:0x3f333333u));
        assert(replacementPixel.code[start+5]==0x3f800000u);
        assert(originalPixel.refs==0);IDirect3DPixelShader9_Release(result);
        reject=true;assert(SUCCEEDED(createPixelShader(wrapper,originalPixel.code.data(),&result)) && result==(IDirect3DPixelShader9*)&originalPixel);IDirect3DPixelShader9_Release(result);reject=false;
    }
    SkyMetadata m={};
    for(const char* removed:{"WindInfo","u_visible_dist","char_pos","u_wvp"}) {
        auto code=fixture(0xfffe0200u,grassNames,sizeof(grassNames));auto bytes=(char*)code.data();
        for(size_t i=0;i+strlen(removed)<code.size()*4;++i)if(!memcmp(bytes+i,removed,strlen(removed))){bytes[i]='X';break;}
        assert(groundKind((const uint32_t*)code.data(),code.size(),&m)==GroundShader::None);
    }
    const char building[]="\0safe_range_color\0weather_intensity\0sam_other0\0sam_diffuse\0PointLightAttrs\0lightmap_scale\0sam_other3\0sam_lightmap\0";
    auto code=fixture(0xffff0300u,building,sizeof(building));assert(groundKind((const uint32_t*)code.data(),code.size(),&m)==GroundShader::None);
    auto good=fixture(0xfffe0300u,grassNames,sizeof(grassNames));groundKind((const uint32_t*)good.data(),good.size(),&m);
    for(size_t n=0;n<good.size();++n){SkyMetadata f={};groundKind((const uint32_t*)good.data(),n,&f);if(n>=1+m.words)assert(makeNoGrass((const uint32_t*)good.data(),n,m,nullptr)==0);}
    std::mt19937 random(0x47524153);
    for(int k=0;k<10000;++k){std::vector<uint32_t> fuzz(random()%256);for(auto& v:fuzz)v=random();if(!fuzz.empty())fuzz[0]=0xfffe0300u;SkyMetadata f={};groundKind(fuzz.data(),fuzz.size(),&f);}
    puts("PASS: production grass/terrain callbacks, shader models 2/3, clipped outputs, flat RGB, off/bypass/failure fallbacks, CTAB preservation, building exclusion, truncation and 10,000 fuzz cases");
}
