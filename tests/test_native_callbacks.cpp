// Executes the actual production callbacks with fake COM objects; no GPU.
#define TEXTURELAB_NATIVE_TEST
#include "../native/texture_lab.cpp"
#include <assert.h>
#ifdef TEXTURELAB_HOST_TEST
#include <thread>
#endif
struct FakeDevice { const IDirect3DDevice9Vtbl* lpVtbl; DWORD value; int writes; bool failReset; ULONG refs; bool nested; DWORD filter; DWORD mip; };
static IDirect3DDevice9Vtbl realTable;
static IDirect3DDevice9* reentryTarget;
static HRESULT STDMETHODCALLTYPE noQI(IDirect3DDevice9*,REFIID,void** out) { *out=nullptr;return E_NOINTERFACE; }
static bool rejectPoint=false;
static HRESULT STDMETHODCALLTYPE setSampler(IDirect3DDevice9* d,DWORD,D3DSAMPLERSTATETYPE type,DWORD value) {
    auto f=(FakeDevice*)d;
    if(type==D3DSAMP_MIPFILTER){if(rejectPoint && value==D3DTEXF_POINT)return D3DERR_INVALIDCALL;f->filter=value;}
    else if(type==D3DSAMP_MAXMIPLEVEL)f->mip=value;
    else f->value=value;
    ++f->writes;return S_OK;
}
static HRESULT STDMETHODCALLTYPE setTexture(IDirect3DDevice9* d,DWORD,IDirect3DBaseTexture9*) {
    auto f=(FakeDevice*)d;
    if(f->nested) { f->nested=false; IDirect3DDevice9_SetTexture(reentryTarget,0,nullptr); }
    return S_OK;
}
static HRESULT STDMETHODCALLTYPE doReset(IDirect3DDevice9* d,D3DPRESENT_PARAMETERS*) {return ((FakeDevice*)d)->failReset?D3DERR_DEVICELOST:S_OK;}
static ULONG STDMETHODCALLTYPE doAdd(IDirect3DDevice9* d) { return ++((FakeDevice*)d)->refs; }
static ULONG STDMETHODCALLTYPE doRelease(IDirect3DDevice9* d) { auto f=(FakeDevice*)d;ULONG n=--f->refs;if(!n) f->lpVtbl=nullptr;return n; }
static HRESULT STDMETHODCALLTYPE begin(IDirect3DDevice9*) { return S_OK; }
static HRESULT STDMETHODCALLTYPE end(IDirect3DDevice9*,IDirect3DStateBlock9**) { return S_OK; }
static UINT textureSize=512;static DWORD textureUsage=0;static DWORD textureLevels=8;
static D3DRESOURCETYPE textureKind=D3DRTYPE_TEXTURE;
static D3DRESOURCETYPE STDMETHODCALLTYPE getType(IDirect3DTexture9*) {return textureKind;}
static DWORD STDMETHODCALLTYPE getCount(IDirect3DTexture9*) {return textureLevels;}
static HRESULT STDMETHODCALLTYPE getDesc(IDirect3DTexture9*,UINT,D3DSURFACE_DESC* out) {memset(out,0,sizeof(*out));out->Width=out->Height=textureSize;out->Usage=textureUsage;return S_OK;}
// Simulate a runtime with a private virtual method after its public factory ABI.
// Its CreateDevice must see the original real pointer/table, including that tail.
struct ExtendedFactoryTable {
    IDirect3D9Vtbl api;
    HRESULT (STDMETHODCALLTYPE *privateMethod)(IDirect3D9*);
};
struct FakeFactory {const IDirect3D9Vtbl* lpVtbl; ULONG refs; int privateCalls; FakeDevice device;};
static FakeFactory* expectedFactory;
static HRESULT STDMETHODCALLTYPE factoryQI(IDirect3D9*,REFIID,void** out){*out=nullptr;return E_NOINTERFACE;}
static ULONG STDMETHODCALLTYPE factoryAdd(IDirect3D9* d){return ++((FakeFactory*)d)->refs;}
static ULONG STDMETHODCALLTYPE factoryRelease(IDirect3D9* d){return --((FakeFactory*)d)->refs;}
static HRESULT STDMETHODCALLTYPE privateCall(IDirect3D9* d){assert(d==(IDirect3D9*)expectedFactory);++expectedFactory->privateCalls;return S_OK;}
static HRESULT STDMETHODCALLTYPE factoryCreate(IDirect3D9* d,UINT,D3DDEVTYPE,HWND,DWORD,D3DPRESENT_PARAMETERS*,IDirect3DDevice9** out){
    assert(d==(IDirect3D9*)expectedFactory);
    auto table=(const ExtendedFactoryTable*)d->lpVtbl;
    assert(SUCCEEDED(table->privateMethod(d)));
    *out=(IDirect3DDevice9*)&expectedFactory->device;return S_OK;
}
static void testFactory(){
    ExtendedFactoryTable table={};table.api.QueryInterface=factoryQI;table.api.AddRef=factoryAdd;
    table.api.Release=factoryRelease;table.api.CreateDevice=factoryCreate;table.privateMethod=privateCall;
    FakeFactory real={&table.api,1,0,{&realTable,0,0,false,1,false}};expectedFactory=&real;
    auto wrapper=attachFactory((IDirect3D9*)&real,false);
    assert((void*)wrapper!=(void*)&real && real.lpVtbl==&table.api);
    IDirect3DDevice9* device=nullptr;
    assert(SUCCEEDED(wrapper->lpVtbl->CreateDevice(wrapper,0,(D3DDEVTYPE)0,nullptr,0,nullptr,&device)));
    assert(real.privateCalls==1 && real.lpVtbl==&table.api);
    assert(device!=(IDirect3DDevice9*)&real.device && real.device.lpVtbl==&realTable);
    assert(IDirect3DDevice9_Release(device)==0);
    assert(wrapper->lpVtbl->Release(wrapper)==0);
}
int main() {
    // Use an isolated test INI and log in Windows' temporary directory.
    GetTempPathW(32600,iniPath);wcscat(iniPath,L"TextureLab_native_test.ini");
    GetTempPathW(32600,logPath);wcscat(logPath,L"TextureLab_native_test.log");
    WritePrivateProfileStringW(L"TextureLab",L"Bias",L"2",iniPath);
    WritePrivateProfileStringW(L"TextureLab",L"Bypass",L"0",iniPath);
    reentryTLS=TlsAlloc(); assert(reentryTLS!=TLS_OUT_OF_INDEXES);
    realTable.QueryInterface=noQI;realTable.SetTexture=setTexture;realTable.SetSamplerState=setSampler;
    realTable.AddRef=doAdd;realTable.Reset=doReset;realTable.Release=doRelease;realTable.BeginStateBlock=begin;realTable.EndStateBlock=end;
    IDirect3DTexture9Vtbl texTable={};texTable.GetType=getType;texTable.GetLevelCount=getCount;texTable.GetLevelDesc=getDesc;
    IDirect3DTexture9 tex={&texTable};
    FakeDevice first={&realTable,0,0,false,1,false}, second={&realTable,0,0,false,1,false};
    auto d=(IDirect3DDevice9*)&first;
    d=attachDevice(d,false);
    assert((void*)d!=(void*)&first);
    assert(first.lpVtbl==&realTable);assert(second.lpVtbl==&realTable);
    void* identity=nullptr;
    assert(SUCCEEDED(d->lpVtbl->QueryInterface(d,IID_IUnknown,&identity)));
    assert(identity==d && first.refs==2);
    assert(IDirect3DDevice9_Release(d)==1 && first.refs==1);
    assert(realTable.SetTexture==setTexture); // Shared runtime table untouched.
    IDirect3DDevice9_SetTexture(d,0,(IDirect3DBaseTexture9*)&tex);
    assert(first.value==floatBits(2.0f));assert(first.writes==1);assert(second.writes==0);
    IDirect3DDevice9_SetSamplerState(d,0,D3DSAMP_MIPMAPLODBIAS,floatBits(-1.0f));
    IDirect3DDevice9_SetTexture(d,0,(IDirect3DBaseTexture9*)&tex);
    assert(first.value==floatBits(1.0f)); // Track original game bias.
    IDirect3DDevice9_SetTexture(d,0,nullptr);assert(first.value==floatBits(-1.0f));
#ifdef TEXTURELAB_HOST_TEST
    int prior=first.writes;
    std::thread worker([&]{mockThreadId=2;IDirect3DDevice9_SetTexture(d,0,(IDirect3DBaseTexture9*)&tex);});
    worker.join();assert(first.writes==prior);assert(ctx(d)->otherThread==1);
#endif
    IDirect3DDevice9_BeginStateBlock(d);int before=first.writes;
    IDirect3DDevice9_SetTexture(d,0,(IDirect3DBaseTexture9*)&tex);assert(first.writes==before);
    IDirect3DStateBlock9* unused=nullptr;IDirect3DDevice9_EndStateBlock(d,&unused);
    first.failReset=true;assert(FAILED(IDirect3DDevice9_Reset(d,nullptr)));before=first.writes;
    IDirect3DDevice9_SetTexture(d,0,(IDirect3DBaseTexture9*)&tex);assert(first.writes==before);
    first.failReset=false;assert(SUCCEEDED(IDirect3DDevice9_Reset(d,nullptr)));
    reentryTarget=d;first.nested=true;IDirect3DDevice9_SetTexture(d,0,(IDirect3DBaseTexture9*)&tex);
    assert(first.value==floatBits(2.0f)); // Nested call did not recursively apply.
    // Real config parsing must retain the stronger bias (old builds clamped to 4).
    WritePrivateProfileStringW(L"TextureLab",L"Bias",L"12",iniPath);
    WritePrivateProfileStringW(L"TextureLab",L"MinTextureSize",L"64",iniPath);
    ctx(d)->config=readConfig();textureSize=64;
    assert(ctx(d)->config.bias==12);
    IDirect3DDevice9_SetTexture(d,0,(IDirect3DBaseTexture9*)&tex);
    assert(first.value==floatBits(12.0f));
    ctx(d)->config.minSize=128;
    IDirect3DDevice9_SetTexture(d,0,(IDirect3DBaseTexture9*)&tex);
    assert(first.value==0); // Too-small textures restore the game's sampler.
    textureSize=512;
    // Strong mode covers autogen mipmaps without forcing LOD/filter state.
    ctx(d)->config.bias=15;ctx(d)->config.minSize=32;ctx(d)->config.includeAutogen=true;
    textureSize=32;textureLevels=1;textureUsage=D3DUSAGE_AUTOGENMIPMAP;
    IDirect3DDevice9_SetTexture(d,0,(IDirect3DBaseTexture9*)&tex);assert(first.value==floatBits(15.0f));
    textureUsage|=D3DUSAGE_RENDERTARGET;
    IDirect3DDevice9_SetTexture(d,0,(IDirect3DBaseTexture9*)&tex);assert(first.value==0);
    textureUsage=D3DUSAGE_AUTOGENMIPMAP;ctx(d)->config.includeAutogen=false;
    IDirect3DDevice9_SetTexture(d,0,(IDirect3DBaseTexture9*)&tex);assert(first.value==0);
    textureUsage=0;textureLevels=8;textureSize=512;
    // A late game write must not undo reduction before the draw.
    ctx(d)->config.allowMipmaps=true;ctx(d)->config.includeAutogen=true;
    IDirect3DDevice9_SetTexture(d,0,(IDirect3DBaseTexture9*)&tex);
    assert(first.filter==D3DTEXF_POINT);
    IDirect3DDevice9_SetSamplerState(d,0,D3DSAMP_MIPMAPLODBIAS,0);
    assert(first.value==floatBits(15.0f));assert(ctx(d)->lateBiasWrites>0);
    IDirect3DDevice9_SetSamplerState(d,0,D3DSAMP_MIPFILTER,D3DTEXF_NONE);
    assert(first.filter==D3DTEXF_POINT);
    IDirect3DDevice9_SetTexture(d,0,nullptr);
    assert(first.value==0 && first.filter==D3DTEXF_NONE);
    // Keep close-up detail coarse, clamp to the available chain, restore game state.
    ctx(d)->config.minimumMip=4;
    IDirect3DDevice9_SetTexture(d,0,(IDirect3DBaseTexture9*)&tex);assert(first.mip==4);
    IDirect3DDevice9_SetSamplerState(d,0,D3DSAMP_MAXMIPLEVEL,0);assert(first.mip==4);
    IDirect3DDevice9_SetTexture(d,0,nullptr);assert(first.mip==0);
    textureLevels=2;IDirect3DDevice9_SetTexture(d,0,(IDirect3DBaseTexture9*)&tex);assert(first.mip==1);
    IDirect3DDevice9_SetTexture(d,0,nullptr);assert(first.mip==0);textureLevels=8;
    // Cubemap skies/reflections use their own interface, only in Potato mode.
    textureKind=D3DRTYPE_CUBETEXTURE;
    IDirect3DDevice9_SetTexture(d,0,(IDirect3DBaseTexture9*)&tex);assert(first.mip==4);
    IDirect3DDevice9_SetTexture(d,0,nullptr);assert(first.mip==0);
    textureUsage=D3DUSAGE_RENDERTARGET;
    IDirect3DDevice9_SetTexture(d,0,(IDirect3DBaseTexture9*)&tex);assert(first.mip==0 && first.value==0);
    textureUsage=0;ctx(d)->config.includeAutogen=false;
    IDirect3DDevice9_SetTexture(d,0,(IDirect3DBaseTexture9*)&tex);assert(first.mip==0 && first.value==0);
    ctx(d)->config.includeAutogen=true;textureKind=D3DRTYPE_TEXTURE;
    // Keep a game's existing mip filter and never force it on a one-level texture.
    IDirect3DDevice9_SetSamplerState(d,0,D3DSAMP_MIPFILTER,D3DTEXF_LINEAR);
    IDirect3DDevice9_SetTexture(d,0,(IDirect3DBaseTexture9*)&tex);assert(first.filter==D3DTEXF_LINEAR);
    IDirect3DDevice9_SetTexture(d,0,nullptr);
    IDirect3DDevice9_SetSamplerState(d,0,D3DSAMP_MIPFILTER,D3DTEXF_NONE);
    textureLevels=1;IDirect3DDevice9_SetTexture(d,0,(IDirect3DBaseTexture9*)&tex);
    assert(first.filter==D3DTEXF_NONE && first.value==0);textureLevels=8;
    // Optional filter rejection must preserve the game's valid HRESULT/value.
    IDirect3DDevice9_SetTexture(d,0,(IDirect3DBaseTexture9*)&tex);
    rejectPoint=true;
    assert(SUCCEEDED(IDirect3DDevice9_SetSamplerState(d,0,D3DSAMP_MIPFILTER,D3DTEXF_NONE)));
    assert(first.filter==D3DTEXF_NONE && !ctx(d)->config.allowMipmaps);rejectPoint=false;
    // Normal/off restores the game's tracked value on the next texture bind.
    ctx(d)->config.enabled=false;IDirect3DDevice9_SetTexture(d,0,(IDirect3DBaseTexture9*)&tex);
    assert(first.value==0);
    assert(IDirect3DDevice9_Release(d)==0);assert(first.lpVtbl==nullptr); // No read after final Release.
    // Stress device creation and final Release, including allocator-address reuse.
    for(int i=0;i<2000;++i) {
        FakeDevice repeat={&realTable,0,0,false,1,false};auto device=(IDirect3DDevice9*)&repeat;
        device=attachDevice(device,false);IDirect3DDevice9_SetTexture(device,0,(IDirect3DBaseTexture9*)&tex);
        assert(IDirect3DDevice9_Release(device)==0);
    }
    // The real device can outlive the wrapper due to resource references.
    FakeDevice retained={&realTable,0,0,false,2,false};
    auto retainedWrapper=attachDevice((IDirect3DDevice9*)&retained,false);
    assert(IDirect3DDevice9_Release(retainedWrapper)==0);
    assert(retained.refs==1 && retained.lpVtbl==&realTable);
    testFactory();
    DeleteFileW(iniPath);DeleteFileW(logPath);TlsFree(reentryTLS);
#ifdef TEXTURELAB_HOST_TEST
    assert(contextAllocations==0);
#endif
    puts("PASS: production COM wrappers, unchanged private runtime tables, real-pointer forwarding, COM identity/refcounts, both sampler call orders, disabled-mipmap correction/fallback, single-level exclusions, sampler restoration, state-block recording, failed/successful reset, re-entry, final release, 2000 create/release cycles");
}
