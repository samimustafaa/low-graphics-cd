#define TEXTURELAB_NATIVE_TEST
#include "../native/texture_lab.cpp"
#include <assert.h>
#include <vector>
#include <memory>
struct Shader {const IDirect3DPixelShader9Vtbl* lpVtbl;ULONG refs;std::vector<DWORD> code;bool generated=false,fail=false;unsigned reads=0;};
static IDirect3DPixelShader9Vtbl table;static IDirect3DDevice9Vtbl deviceTable;
static std::vector<std::unique_ptr<Shader>> objects;static Shader* bound=nullptr;
static unsigned creates=0;static bool rejectCreate=false,rejectBind=false;
static ULONG STDMETHODCALLTYPE add(IDirect3DPixelShader9* p){return ++((Shader*)p)->refs;}
static ULONG STDMETHODCALLTYPE drop(IDirect3DPixelShader9* p){assert(((Shader*)p)->refs);return --((Shader*)p)->refs;}
static HRESULT STDMETHODCALLTYPE read(IDirect3DPixelShader9* p,void* out,UINT* bytes) {
 auto s=(Shader*)p;++s->reads;if(s->fail)return D3DERR_INVALIDCALL;
 if(out){assert(*bytes>=s->code.size()*4);memcpy(out,s->code.data(),s->code.size()*4);}
 *bytes=(UINT)s->code.size()*4;return S_OK;
}
static Shader* object(const std::vector<DWORD>& code,bool generated=false) {
 objects.emplace_back(new Shader{&table,1,code,generated});return objects.back().get();
}
static HRESULT STDMETHODCALLTYPE create(IDirect3DDevice9*,const DWORD* code,IDirect3DPixelShader9** out) {
 ++creates;if(rejectCreate){*out=nullptr;return D3DERR_INVALIDCALL;}
 SkyMetadata m={};size_t count=2+((code[1]>>16)&0x7fff)+10;
 assert(findSkyMetadata((const uint32_t*)code,count,&m));
 auto result=object(std::vector<DWORD>(code,code+graySkyWordCount(m)),true);*out=(IDirect3DPixelShader9*)result;return S_OK;
}
static HRESULT STDMETHODCALLTYPE bind(IDirect3DDevice9*,IDirect3DPixelShader9* p) {
 auto s=(Shader*)p;if(s && s->generated && rejectBind)return D3DERR_INVALIDCALL;
 if(s)add(p);if(bound)drop((IDirect3DPixelShader9*)bound);bound=s;return S_OK;
}
static HRESULT STDMETHODCALLTYPE get(IDirect3DDevice9*,IDirect3DPixelShader9** out){*out=(IDirect3DPixelShader9*)bound;if(*out)add(*out);return S_OK;}
static std::vector<DWORD> fixture(const char* names,size_t bytes) {
 size_t words=1+(bytes+3)/4;std::vector<DWORD> code(3+words,0);
 code[0]=0xffff0300u;code[1]=0xfffe|((DWORD)words<<16);code[2]=0x42415443;
 memcpy(code.data()+3,names,bytes);code.back()=0xffff;return code;
}
int main(){
 reentryTLS=TlsAlloc();table.AddRef=add;table.Release=drop;table.GetFunction=read;
 deviceTable.CreatePixelShader=create;deviceTable.SetPixelShader=bind;deviceTable.GetPixelShader=get;
 IDirect3DDevice9 real={&deviceTable};DeviceContext c={};c.real=&real;c.original=&deviceTable;c.config.enabled=true;c.config.neutralSky=true;
 auto wrapper=(IDirect3DDevice9*)&c;
 const char names[]="\0skycolormid\0skycolorhigh\0bk_cloud_color\0cloud_thickness\0";
 const char terrain[]="\0safe_range_color\0char_pos\0sky_color\0weather_intensity\0sam_other0\0";
 auto source=object(fixture(names,sizeof(names)));auto floor=object(fixture(terrain,sizeof(terrain)));
 // Simulate shaders created directly by the native device, never through our factory callback.
 for(bool black:{false,true}) {
  c.config.blackSky=black;clearSkyBindings(&c);unsigned before=creates;
  assert(SUCCEEDED(setPixelShader(wrapper,(IDirect3DPixelShader9*)source)) && bound!=source && creates==before+1);
  size_t start=bound->code.size()-10;for(int i=2;i<5;++i)assert(bound->code[start+i]==(black?0u:0x3f000000u));
  unsigned reads=source->reads;
  for(int n=0;n<1000;++n)assert(SUCCEEDED(setPixelShader(wrapper,(IDirect3DPixelShader9*)source)));
  assert(source->reads==reads && creates==before+1); // Cached: no bytecode queries or allocation per bind.
  IDirect3DPixelShader9* logical=nullptr;assert(SUCCEEDED(getPixelShader(wrapper,&logical)) && logical==(IDirect3DPixelShader9*)source);drop(logical);
  assert(SUCCEEDED(setPixelShader(wrapper,(IDirect3DPixelShader9*)floor)) && bound==floor && creates==before+1);
  c.config.neutralSky=false;assert(SUCCEEDED(setPixelShader(wrapper,(IDirect3DPixelShader9*)source)) && bound==source);c.config.neutralSky=true;
 }
 for(int mode=0;mode<6;++mode) {
  clearSkyBindings(&c);rejectCreate=mode==0;rejectBind=mode==1;source->fail=mode==2;c.blocked=mode==3;c.recording=mode==4;c.config.bypass=mode==5;
  assert(SUCCEEDED(setPixelShader(wrapper,(IDirect3DPixelShader9*)source)) && bound==source);
 }
 rejectCreate=rejectBind=false;source->fail=false;c.blocked=c.recording=0;c.config.bypass=false;
 clearSkyBindings(&c);assert(SUCCEEDED(setPixelShader(wrapper,(IDirect3DPixelShader9*)source)));
 auto ready=bound;unsigned before=creates;assert(SUCCEEDED(setPixelShader(wrapper,(IDirect3DPixelShader9*)ready)) && creates==before); // No double replacement.
 setPixelShader(wrapper,nullptr);clearSkyBindings(&c);
 assert(source->refs==1 && floor->refs==1);
 for(const auto& s:objects)if(s->generated)assert(s->refs==0);
 puts("PASS: native-created sky bind override, Gray/Black/Normal, floor exclusion, shader identity, 1000 cached binds, failure/reentry guards and reference cleanup");
}
