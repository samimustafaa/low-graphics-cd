// Texture Lab 1.6.10. Public COM forwarding wrappers. System objects, private
// runtime layouts and runtime vtables are never modified. Original MIT source.
#define CINTERFACE
#define COBJMACROS
#define WIN32_LEAN_AND_MEAN
#define INITGUID
#ifdef TEXTURELAB_HOST_TEST
#include "../tests/win32_mock.h"
#else
#include <windows.h>
#include <d3d9.h>
#endif
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <wchar.h>
#include <stdio.h>
#include "ground_shader.h"
#include "structure_shader.h"


static HMODULE selfModule, systemD3D;
static INIT_ONCE initOnce = INIT_ONCE_STATIC_INIT;
static wchar_t iniPath[32768], logPath[32768];
static DWORD reentryTLS = TLS_OUT_OF_INDEXES;
static void logLine(const char* text) {
    HANDLE f=CreateFileW(logPath,FILE_APPEND_DATA,FILE_SHARE_READ|FILE_SHARE_WRITE,
                         nullptr,OPEN_ALWAYS,FILE_ATTRIBUTE_NORMAL,nullptr);
    if(f!=INVALID_HANDLE_VALUE) {
        DWORD written; WriteFile(f,text,(DWORD)strlen(text),&written,nullptr);
        WriteFile(f,"\r\n",2,&written,nullptr); CloseHandle(f);
    }
}
static BOOL CALLBACK initialize(PINIT_ONCE, PVOID, PVOID*) {
    wchar_t path[MAX_PATH]; UINT n=GetSystemDirectoryW(path,MAX_PATH);
    if(n && n<MAX_PATH-11) {
        wcscat(path,L"\\d3d9.dll"); systemD3D=LoadLibraryW(path);
    }
    DWORD length=GetModuleFileNameW(selfModule,iniPath,32768);
    if(length && length<32700) {
        wchar_t* slash=wcsrchr(iniPath,L'\\');
        if(slash) {
            slash[1]=0; wcscpy(logPath,iniPath);
            wcscat(iniPath,L"CD_TextureLab.ini"); wcscat(logPath,L"CD_TextureLab.log");
        }
    }
    reentryTLS=TlsAlloc();
    HMODULE pinned;
    GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,
                      (LPCWSTR)selfModule,&pinned);
    char line[160]; snprintf(line,sizeof(line),"TextureLab 1.6.10 loaded pid=%lu system_runtime=%s",GetCurrentProcessId(),systemD3D?"ok":"FAILED");
    logLine(line); return TRUE;
}
static FARPROC resolve(const char* name) {
    InitOnceExecuteOnce(&initOnce,initialize,nullptr,nullptr);
    return systemD3D?GetProcAddress(systemD3D,name):nullptr;
}
struct Config { bool enabled; int bias; UINT minSize; bool bypass; bool neutralSky, includeAutogen, allowMipmaps; UINT minimumMip; bool collectStats; bool blackSky; bool flatGround; bool opaqueStructures; };
static Config readConfig() {
    int bias=(int)GetPrivateProfileIntW(L"TextureLab",L"Bias",2,iniPath);
    int size=(int)GetPrivateProfileIntW(L"TextureLab",L"MinTextureSize",256,iniPath);
    int minimumMip=(int)GetPrivateProfileIntW(L"TextureLab",L"MinMipLevel",0,iniPath);
    bool bypass=GetPrivateProfileIntW(L"TextureLab",L"Bypass",0,iniPath)!=0;
    return {GetPrivateProfileIntW(L"TextureLab",L"Enabled",1,iniPath)!=0 && !bypass,
            bias<0?0:(bias>15?15:bias),(UINT)(size<32?32:(size>4096?4096:size)),bypass,
            GetPrivateProfileIntW(L"TextureLab",L"NeutralSky",0,iniPath)!=0,
            GetPrivateProfileIntW(L"TextureLab",L"IncludeAutogen",0,iniPath)!=0,
            GetPrivateProfileIntW(L"TextureLab",L"ForceMipFilter",0,iniPath)!=0,
            (UINT)(minimumMip<0?0:(minimumMip>4?4:minimumMip)),
            GetPrivateProfileIntW(L"TextureLab",L"CollectStats",0,iniPath)!=0,
            GetPrivateProfileIntW(L"TextureLab",L"BlackSky",0,iniPath)!=0,
            GetPrivateProfileIntW(L"TextureLab",L"FlatGround",0,iniPath)!=0,
            GetPrivateProfileIntW(L"TextureLab",L"OpaqueStructures",0,iniPath)!=0};
}
struct CallGuard {
    bool outer;
    CallGuard():outer(reentryTLS!=TLS_OUT_OF_INDEXES && TlsGetValue(reentryTLS)==nullptr) {
        if(outer && !TlsSetValue(reentryTLS,(PVOID)1)) outer=false;
    }
    ~CallGuard() { if(outer) TlsSetValue(reentryTLS,nullptr); }
};
constexpr size_t deviceSlots=sizeof(IDirect3DDevice9ExVtbl)/sizeof(void*);
constexpr size_t factorySlots=sizeof(IDirect3D9ExVtbl)/sizeof(void*);
struct Sampler {
    DWORD requested; bool applied; DWORD appliedValue;
    bool eligible, filterApplied; DWORD requestedFilter, appliedFilter;
    DWORD requestedMip, appliedMip; bool mipApplied; UINT maxMip;
};
struct SkyBinding {IDirect3DPixelShader9* source;IDirect3DPixelShader9* replacement;};
struct DeviceContext {
    const IDirect3DDevice9Vtbl* lpVtbl;
    IDirect3DDevice9* real; const IDirect3DDevice9Vtbl* original;
    void* entries[deviceSlots]; volatile LONG refs; bool ex;
    volatile LONG callbacks, dead, blocked, recording, renderThread;
    Config config; ULONGLONG lastPoll, nextLog;
    unsigned long eligibleBinds, modifications, failures, otherThread, shaderChecks, graySkies, lateBiasWrites, disabledMipWrites, mipChanges, noMipBinds, mipFloorChanges, flatGrounds, hiddenGrass;
    Sampler samplers[16];
    SkyBinding skyBindings[256];
    unsigned long skyBindReads, skyBindMatches, skyBindMisses;
};
struct FactoryContext {
    const IDirect3D9Vtbl* lpVtbl;
    IDirect3D9* real; const IDirect3D9Vtbl* original;
    void* entries[factorySlots]; volatile LONG refs; bool ex;
    volatile LONG callbacks, dead;
};
static_assert(offsetof(DeviceContext,lpVtbl)==0,"COM interface must be first");
static_assert(offsetof(FactoryContext,lpVtbl)==0,"COM interface must be first");
template<class Context> struct Hold {
    Context* c;
    explicit Hold(Context* ptr):c(ptr) { InterlockedIncrement(&c->callbacks); }
    ~Hold() { if(!InterlockedDecrement(&c->callbacks) && c->dead) HeapFree(GetProcessHeap(),0,c); }
};
static DeviceContext* ctx(IDirect3DDevice9* d) { return (DeviceContext*)d; }
static FactoryContext* ctx(IDirect3D9* d) { return (FactoryContext*)d; }
static ULONG STDMETHODCALLTYPE addDevice(IDirect3DDevice9* d) {
    auto c=ctx(d); c->original->AddRef(c->real); return (ULONG)InterlockedIncrement(&c->refs);
}
static ULONG STDMETHODCALLTYPE addFactory(IDirect3D9* d) {
    auto c=ctx(d); c->original->AddRef(c->real); return (ULONG)InterlockedIncrement(&c->refs);
}
static HRESULT STDMETHODCALLTYPE queryDevice(IDirect3DDevice9* d,REFIID iid,void** out) {
    if(!out) return E_POINTER;
    auto c=ctx(d); Hold<DeviceContext> hold(c);
    if(IsEqualIID(iid,IID_IUnknown) || IsEqualIID(iid,IID_IDirect3DDevice9) ||
       (c->ex && IsEqualIID(iid,IID_IDirect3DDevice9Ex))) {
        addDevice(d); *out=d; return S_OK;
    }
    // Unknown/private interfaces stay native; never pretend to implement them.
    return c->original->QueryInterface(c->real,iid,out);
}
static HRESULT STDMETHODCALLTYPE queryFactory(IDirect3D9* d,REFIID iid,void** out) {
    if(!out) return E_POINTER;
    auto c=ctx(d); Hold<FactoryContext> hold(c);
    if(IsEqualIID(iid,IID_IUnknown) || IsEqualIID(iid,IID_IDirect3D9) ||
       (c->ex && IsEqualIID(iid,IID_IDirect3D9Ex))) {
        addFactory(d); *out=d; return S_OK;
    }
    return c->original->QueryInterface(c->real,iid,out);
}
static HRESULT STDMETHODCALLTYPE createPixelShader(IDirect3DDevice9* d,const DWORD* code,IDirect3DPixelShader9** out) {
    auto c=ctx(d); Hold<DeviceContext> hold(c); CallGuard entry;
    HRESULT hr=c->original->CreatePixelShader(c->real,code,out);
    if(!entry.outer || FAILED(hr) || !out || !*out || !c->config.enabled || !c->config.neutralSky || c->config.bypass)return hr;
    // Normal blue sky keeps the terrain material/shading and its own colors.
    // Potato sampler reduction still removes fine detail; grass is handled by VS.
    ++c->shaderChecks;
    UINT bytes=0;
    if(FAILED(IDirect3DPixelShader9_GetFunction(*out,nullptr,&bytes)) || bytes<8 || bytes>1024*1024 || bytes%4)return hr;
    UINT capacity=bytes;
    auto original=(DWORD*)HeapAlloc(GetProcessHeap(),0,capacity);
    if(!original)return hr;
    SkyMetadata match={};bool terrain=false;
    if(SUCCEEDED(IDirect3DPixelShader9_GetFunction(*out,original,&bytes)) && bytes<=capacity && bytes%4==0 &&
       ((c->config.flatGround && (terrain=groundKind((const uint32_t*)original,bytes/4,&match)==GroundShader::Terrain)) ||
        (c->config.neutralSky && findSkyMetadata((const uint32_t*)original,bytes/4,&match)))) {
        size_t words=graySkyWordCount(match);
        auto gray=(DWORD*)HeapAlloc(GetProcessHeap(),0,words*4);
        if(gray) {
            if(terrain)makeFlatGround(match,(uint32_t*)gray);else makeGraySky(match,(uint32_t*)gray,c->config.blackSky);IDirect3DPixelShader9* replacement=nullptr;
            HRESULT replacementHR=c->original->CreatePixelShader(c->real,gray,&replacement);
            if(SUCCEEDED(replacementHR) && replacement) {
                IDirect3DPixelShader9_Release(*out);*out=replacement;if(terrain)++c->flatGrounds;else ++c->graySkies;
                logLine(terrain?"Dark flat ground shader created for Gray sky; terrain metadata matched.":c->config.blackSky?"Black sky shader created; sky metadata matched.":"Neutral gray sky shader created; sky metadata matched.");
            } else logLine("Solid shader rejected; original shader retained.");
            HeapFree(GetProcessHeap(),0,gray);
        }
    }
    HeapFree(GetProcessHeap(),0,original);return hr;
}
static HRESULT STDMETHODCALLTYPE createVertexShader(IDirect3DDevice9* d,const DWORD* code,IDirect3DVertexShader9** out) {
    auto c=ctx(d);Hold<DeviceContext> hold(c);CallGuard entry;
    HRESULT hr=c->original->CreateVertexShader(c->real,code,out);
    if(!entry.outer || FAILED(hr) || !out || !*out || !c->config.enabled || !c->config.flatGround || c->config.bypass)return hr;
    UINT bytes=0;
    if(FAILED(IDirect3DVertexShader9_GetFunction(*out,nullptr,&bytes)) || bytes<8 || bytes>1024*1024 || bytes%4)return hr;
    UINT capacity=bytes;auto original=(DWORD*)HeapAlloc(GetProcessHeap(),0,capacity);
    if(!original)return hr;
    SkyMetadata match={};
    if(SUCCEEDED(IDirect3DVertexShader9_GetFunction(*out,original,&bytes)) && bytes<=capacity && bytes%4==0 &&
       groundKind((const uint32_t*)original,bytes/4,&match)==GroundShader::Grass) {
        size_t words=makeNoGrass((const uint32_t*)original,bytes/4,match,nullptr);
        auto hidden=words?(DWORD*)HeapAlloc(GetProcessHeap(),0,words*4):nullptr;
        if(hidden) {
            makeNoGrass((const uint32_t*)original,bytes/4,match,(uint32_t*)hidden);
            IDirect3DVertexShader9* replacement=nullptr;
            HRESULT result=c->original->CreateVertexShader(c->real,hidden,&replacement);
            if(SUCCEEDED(result) && replacement) {
                IDirect3DVertexShader9_Release(*out);*out=replacement;++c->hiddenGrass;
                logLine("No grass shader created; grass metadata matched.");
            } else logLine("No grass shader rejected; original shader retained.");
            HeapFree(GetProcessHeap(),0,hidden);
        }
    }
    HeapFree(GetProcessHeap(),0,original);return hr;
}
#ifndef TEXTURELAB_HOST_TEST
#include "public_forwarders.inc"
#endif
static DWORD floatBits(float f) { DWORD r; memcpy(&r,&f,4); return r; }
static void poll(DeviceContext* c) {
    if(!c->config.collectStats)return; // Default: no render-path disk IO or timers.
    ULONGLONG now=GetTickCount64();
    // Settings change only between game sessions; no per-bind INI reads.
    if(now>=c->nextLog) {
        char line[512]; snprintf(line,sizeof(line),"pid=%lu thread=%ld bias=%d enabled=%d eligible=%lu changed=%lu failed=%lu other_thread=%lu blocked=%ld shaders=%lu gray_skies=%lu late_bias=%lu disabled_mip=%lu mip_changes=%lu no_mips=%lu mip_floor=%lu flat_ground=%lu hidden_grass=%lu sky_bind_reads=%lu sky_bind_matches=%lu sky_bind_misses=%lu",
            GetCurrentProcessId(),c->renderThread,c->config.bias,c->config.enabled,c->eligibleBinds,c->modifications,c->failures,c->otherThread,c->blocked,c->shaderChecks,c->graySkies,c->lateBiasWrites,c->disabledMipWrites,c->mipChanges,c->noMipBinds,c->mipFloorChanges,c->flatGrounds,c->hiddenGrass,c->skyBindReads,c->skyBindMatches,c->skyBindMisses);
        logLine(line); c->nextLog=now+10000;
    }
}
static bool ownsThread(DeviceContext* c) {
    LONG thread=(LONG)GetCurrentThreadId();
    LONG owner=InterlockedCompareExchange(&c->renderThread,thread,0);
    if(owner && owner!=thread) { InterlockedIncrement((volatile LONG*)&c->otherThread); return false; }
    return true;
}
#include "sky_binding.inc"
static DWORD desired(DeviceContext* c,DWORD slot,bool eligible) {
    DWORD original=c->samplers[slot].requested;
    if(!c->config.enabled || !eligible || !c->config.bias) return original;
    float f; memcpy(&f,&original,4);
    // Reject NaN/infinity without requiring a C++ maths runtime.
    if((original&0x7f800000)==0x7f800000) return original;
    f+=(float)c->config.bias; if(f>15) f=15; if(f< -16) f=-16;
    return floatBits(f);
}
static void apply(DeviceContext* c,DWORD slot,DWORD value) {
    HRESULT hr=c->original->SetSamplerState(c->real,slot,D3DSAMP_MIPMAPLODBIAS,value);
    if(SUCCEEDED(hr)) {
        c->samplers[slot].applied=true; c->samplers[slot].appliedValue=value;
        if(value!=c->samplers[slot].requested) ++c->modifications;
    } else {
        ++c->failures; InterlockedExchange(&c->blocked,1);
        logLine("Sampler override rejected; extra overrides suspended until a successful device reset.");
    }
}
static DWORD desiredFilter(DeviceContext* c,Sampler& state,bool eligible) {
    return c->config.enabled && c->config.bias && c->config.allowMipmaps && eligible &&
           state.requestedFilter==D3DTEXF_NONE ? (DWORD)D3DTEXF_POINT : state.requestedFilter;
}
static void applyFilter(DeviceContext* c,DWORD slot,bool eligible) {
    auto& state=c->samplers[slot];DWORD value=desiredFilter(c,state,eligible);
    if(!((value!=state.requestedFilter) || (state.filterApplied && state.appliedFilter!=state.requestedFilter)))return;
    if(state.filterApplied && state.appliedFilter==value)return;
    HRESULT hr=c->original->SetSamplerState(c->real,slot,D3DSAMP_MIPFILTER,value);
    if(SUCCEEDED(hr)){state.filterApplied=true;state.appliedFilter=value;++c->mipChanges;}
    else {
        // Optional filter failed: retry the game's original value and turn only
        // this option off. Do not convert a valid game call into an error.
        c->original->SetSamplerState(c->real,slot,D3DSAMP_MIPFILTER,state.requestedFilter);
        c->config.allowMipmaps=false;state.filterApplied=false;++c->failures;
        logLine("Optional mip filter rejected; original filter retained and option suspended.");
    }
}
static DWORD desiredMip(DeviceContext* c,Sampler& state,bool eligible) {
    if(!c->config.enabled || !c->config.allowMipmaps || !eligible || !state.maxMip)return state.requestedMip;
    UINT floor=c->config.minimumMip<state.maxMip?c->config.minimumMip:state.maxMip;
    return state.requestedMip>floor?state.requestedMip:floor;
}
static void applyMip(DeviceContext* c,DWORD slot,bool eligible) {
    auto& state=c->samplers[slot];DWORD value=desiredMip(c,state,eligible);
    if(value==state.requestedMip && !(state.mipApplied && state.appliedMip!=state.requestedMip))return;
    if(state.mipApplied && state.appliedMip==value)return;
    HRESULT hr=c->original->SetSamplerState(c->real,slot,D3DSAMP_MAXMIPLEVEL,value);
    if(SUCCEEDED(hr)){state.mipApplied=true;state.appliedMip=value;++c->mipFloorChanges;}
    else{
        c->original->SetSamplerState(c->real,slot,D3DSAMP_MAXMIPLEVEL,state.requestedMip);
        state.mipApplied=false;c->config.minimumMip=0;++c->failures;
        logLine("Close-range mip limit rejected; original level retained and option suspended.");
    }
}
static HRESULT STDMETHODCALLTYPE texture(IDirect3DDevice9* d,DWORD slot,IDirect3DBaseTexture9* t) {
    auto c=ctx(d); Hold<DeviceContext> hold(c); CallGuard entry;
    HRESULT hr=c->original->SetTexture(c->real,slot,t);
    if(!entry.outer || FAILED(hr) || slot>=16 || c->blocked || c->recording || !ownsThread(c)) return hr;
    poll(c);
    bool eligible=false;
    // Normal/off sessions avoid metadata queries entirely.
    if(!c->config.enabled || !c->config.bias) {
        auto& state=c->samplers[slot];state.eligible=false;
        if(state.applied && state.appliedValue!=state.requested)apply(c,slot,state.requested);
        applyFilter(c,slot,false);applyMip(c,slot,false);return hr;
    }
    UINT levels=t?IDirect3DBaseTexture9_GetLevelCount(t):0;
    D3DRESOURCETYPE kind=t?IDirect3DBaseTexture9_GetType(t):(D3DRESOURCETYPE)0;
    bool cube=kind==D3DRTYPE_CUBETEXTURE && c->config.includeAutogen;
    if(t && (kind==D3DRTYPE_TEXTURE || cube) && (levels>1 || c->config.includeAutogen)) {
        D3DSURFACE_DESC desc;
        HRESULT description=cube?
            IDirect3DCubeTexture9_GetLevelDesc((IDirect3DCubeTexture9*)t,0,&desc):
            IDirect3DTexture9_GetLevelDesc((IDirect3DTexture9*)t,0,&desc);
        if(SUCCEEDED(description))
            eligible=!(desc.Usage&(D3DUSAGE_RENDERTARGET|D3DUSAGE_DEPTHSTENCIL)) &&
                (!(desc.Usage&D3DUSAGE_AUTOGENMIPMAP) || c->config.includeAutogen) &&
                (levels>1 || (c->config.includeAutogen && (desc.Usage&D3DUSAGE_AUTOGENMIPMAP))) &&
                desc.Width>=c->config.minSize && desc.Height>=c->config.minSize;
    }
    if(eligible) ++c->eligibleBinds;else if(t && levels<=1)++c->noMipBinds;
    c->samplers[slot].eligible=eligible;
    c->samplers[slot].maxMip=eligible && levels>1?levels-1:0;
    auto& sampler=c->samplers[slot]; DWORD value=desired(c,slot,eligible);
    // Write on eligible binds (state blocks may change actual runtime values).
    // Restore only if this helper has previously changed this sampler.
    if((eligible && c->config.enabled && c->config.bias) ||
       (sampler.applied && sampler.appliedValue!=sampler.requested)) apply(c,slot,value);
    if(!c->blocked){applyFilter(c,slot,eligible);applyMip(c,slot,eligible);}
    return hr;
}
static HRESULT STDMETHODCALLTYPE sampler(IDirect3DDevice9* d,DWORD slot,D3DSAMPLERSTATETYPE type,DWORD value) {
    auto c=ctx(d); Hold<DeviceContext> hold(c); CallGuard entry;
    bool track=entry.outer && slot<16 && !c->blocked && !c->recording &&
        (!c->renderThread || (DWORD)c->renderThread==GetCurrentThreadId());
    if(!track || (type!=D3DSAMP_MIPMAPLODBIAS && type!=D3DSAMP_MIPFILTER && type!=D3DSAMP_MAXMIPLEVEL))
        return c->original->SetSamplerState(c->real,slot,type,value);
    auto& state=c->samplers[slot];Sampler previous=state;
    if(type==D3DSAMP_MIPMAPLODBIAS)state.requested=value;
    else if(type==D3DSAMP_MIPFILTER)state.requestedFilter=value;else state.requestedMip=value;
    DWORD effective=type==D3DSAMP_MIPMAPLODBIAS?
        (c->config.includeAutogen?desired(c,slot,state.eligible):value):
        (type==D3DSAMP_MIPFILTER?desiredFilter(c,state,state.eligible):desiredMip(c,state,state.eligible));
    // Handle both call orders: SetSamplerState may follow SetTexture.
    HRESULT hr=c->original->SetSamplerState(c->real,slot,type,effective);
    if(FAILED(hr)) {
        state=previous;
        if(effective!=value){
            ++c->failures;
            if(type==D3DSAMP_MIPFILTER)c->config.allowMipmaps=false;
            else if(type==D3DSAMP_MAXMIPLEVEL)c->config.minimumMip=0;else InterlockedExchange(&c->blocked,1);
            hr=c->original->SetSamplerState(c->real,slot,type,value);
            if(SUCCEEDED(hr)) {
                if(type==D3DSAMP_MIPMAPLODBIAS){state.requested=value;state.applied=false;}
                else if(type==D3DSAMP_MIPFILTER){state.requestedFilter=value;state.filterApplied=false;}
                else{state.requestedMip=value;state.mipApplied=false;}
            }
        }
        return hr;
    }
    if(type==D3DSAMP_MIPMAPLODBIAS){
        state.applied=effective!=value;state.appliedValue=effective;
        if(effective!=value){++c->modifications;++c->lateBiasWrites;}
    }else if(type==D3DSAMP_MIPFILTER){
        state.filterApplied=effective!=value;state.appliedFilter=effective;
        if(value==D3DTEXF_NONE)++c->disabledMipWrites;
        if(effective!=value)++c->mipChanges;
    }else{state.mipApplied=effective!=value;state.appliedMip=effective;if(effective!=value)++c->mipFloorChanges;}
    return hr;
}

static HRESULT STDMETHODCALLTYPE beginBlock(IDirect3DDevice9* d) {
    auto c=ctx(d); Hold<DeviceContext> hold(c);
    // Restore our own overrides before recording starts, so state blocks do
    // not capture helper values or carry them onto an excluded render target.
    if(!c->recording && !c->blocked && (!c->renderThread || (DWORD)c->renderThread==GetCurrentThreadId())) {
        for(DWORD slot=0;slot<16;++slot){
            auto& state=c->samplers[slot];
            if(state.applied && state.appliedValue!=state.requested)apply(c,slot,state.requested);
            if(!c->blocked){applyFilter(c,slot,false);applyMip(c,slot,false);}
            state.eligible=false;
        }
    }
    HRESULT hr=c->original->BeginStateBlock(c->real); if(SUCCEEDED(hr)){InterlockedExchange(&c->recording,1);for(auto& s:c->samplers)s.eligible=false;} return hr;
}
static HRESULT STDMETHODCALLTYPE endBlock(IDirect3DDevice9* d,IDirect3DStateBlock9** out) {
    auto c=ctx(d); Hold<DeviceContext> hold(c);
    HRESULT hr=c->original->EndStateBlock(c->real,out); if(SUCCEEDED(hr)){InterlockedExchange(&c->recording,0);for(auto& s:c->samplers){s.eligible=false;s.applied=false;s.filterApplied=false;s.mipApplied=false;}} return hr;
}
static void afterReset(DeviceContext* c,HRESULT hr) {
    if(SUCCEEDED(hr)) {
        memset(c->samplers,0,sizeof(c->samplers)); InterlockedExchange(&c->recording,0);
        InterlockedExchange(&c->renderThread,0); InterlockedExchange(&c->blocked,0);
        logLine("Device reset succeeded; bias tracking reset.");
    } else logLine("Device reset failed; extra texture calls remain disabled.");
}
static HRESULT STDMETHODCALLTYPE reset(IDirect3DDevice9* d,D3DPRESENT_PARAMETERS* p) {
    auto c=ctx(d); Hold<DeviceContext> hold(c); InterlockedExchange(&c->blocked,1);
    // Shader objects survive Reset; retain cached shader references.
    HRESULT hr=c->original->Reset(c->real,p); afterReset(c,hr); return hr;
}
static HRESULT STDMETHODCALLTYPE resetEx(IDirect3DDevice9Ex* d,D3DPRESENT_PARAMETERS* p,D3DDISPLAYMODEEX* mode) {
    auto c=ctx((IDirect3DDevice9*)d); Hold<DeviceContext> hold(c); InterlockedExchange(&c->blocked,1);
    HRESULT hr=((const IDirect3DDevice9ExVtbl*)c->original)->ResetEx((IDirect3DDevice9Ex*)c->real,p,mode); afterReset(c,hr); return hr;
}
static ULONG STDMETHODCALLTYPE releaseDevice(IDirect3DDevice9* d) {
    auto c=ctx(d); Hold<DeviceContext> hold(c);
    ULONG refs=(ULONG)InterlockedDecrement(&c->refs);
    if(!refs){
        if(c->config.neutralSky || c->config.opaqueStructures){char summary[160];snprintf(summary,sizeof(summary),"Sky bind summary: reads=%lu matches=%lu unknown=%lu",c->skyBindReads,c->skyBindMatches,c->skyBindMisses);logLine(summary);}
        clearSkyBindings(c);InterlockedExchange(&c->dead,1);
    }
    c->original->Release(c->real);return refs;
}
static void fillDeviceTable(DeviceContext*);
static void fillFactoryTable(FactoryContext*);
static IDirect3DDevice9* attachDevice(IDirect3DDevice9* d,bool knownEx) {
    auto c=(DeviceContext*)HeapAlloc(GetProcessHeap(),HEAP_ZERO_MEMORY,sizeof(DeviceContext));
    if(!c) { logLine("Device wrapper allocation failed; forwarding original."); return d; }
    c->original=d->lpVtbl; c->real=d; c->refs=1; c->ex=knownEx;
    c->config=readConfig(); fillDeviceTable(c);
    logLine(!c->config.neutralSky?"Requested SKY: Normal (original blue).":c->config.blackSky?"Requested SKY: Black (ground unaffected).":"Requested SKY: Gray (ground unaffected).");
    c->lpVtbl=(const IDirect3DDevice9Vtbl*)c->entries;
    logLine(knownEx?"Public D3D9Ex device wrapper ready; runtime untouched.":"Public D3D9 device wrapper ready; runtime untouched.");
    return (IDirect3DDevice9*)c;
}
static HRESULT STDMETHODCALLTYPE createDevice(IDirect3D9* d,UINT a,D3DDEVTYPE t,HWND w,DWORD flags,D3DPRESENT_PARAMETERS* p,IDirect3DDevice9** out) {
    auto c=ctx(d); Hold<FactoryContext> hold(c);
    logLine("CreateDevice: entering system runtime.");
    HRESULT hr=c->original->CreateDevice(c->real,a,t,w,flags,p,out);
    logLine(SUCCEEDED(hr)?"CreateDevice: system runtime succeeded.":"CreateDevice: system runtime failed.");
    if(SUCCEEDED(hr) && out && *out && !readConfig().bypass) *out=attachDevice(*out,false);
    return hr;
}
static HRESULT STDMETHODCALLTYPE createDeviceEx(IDirect3D9Ex* d,UINT a,D3DDEVTYPE t,HWND w,DWORD flags,D3DPRESENT_PARAMETERS* p,D3DDISPLAYMODEEX* mode,IDirect3DDevice9Ex** out) {
    auto c=ctx((IDirect3D9*)d); Hold<FactoryContext> hold(c);
    logLine("CreateDeviceEx: entering system runtime.");
    HRESULT hr=((const IDirect3D9ExVtbl*)c->original)->CreateDeviceEx((IDirect3D9Ex*)c->real,a,t,w,flags,p,mode,out);
    logLine(SUCCEEDED(hr)?"CreateDeviceEx: system runtime succeeded.":"CreateDeviceEx: system runtime failed.");
    if(SUCCEEDED(hr) && out && *out && !readConfig().bypass) *out=(IDirect3DDevice9Ex*)attachDevice((IDirect3DDevice9*)*out,true);
    return hr;
}
static ULONG STDMETHODCALLTYPE releaseFactory(IDirect3D9* d) {
    auto c=ctx(d); Hold<FactoryContext> hold(c);
    c->original->Release(c->real);
    ULONG refs=(ULONG)InterlockedDecrement(&c->refs);
    if(!refs) InterlockedExchange(&c->dead,1); return refs;
}
#ifndef TEXTURELAB_HOST_TEST
#include "public_tables.inc"
#else
// The portable test double exposes only the methods used in callback tests.
static void fillDeviceTable(DeviceContext* c) {
    IDirect3DDevice9ExVtbl t={}; t.QueryInterface=queryDevice;t.AddRef=addDevice;t.Release=releaseDevice;
    t.SetTexture=texture;t.SetSamplerState=sampler;t.Reset=reset;t.ResetEx=resetEx;
    t.BeginStateBlock=beginBlock;t.EndStateBlock=endBlock;t.CreatePixelShader=createPixelShader;t.CreateVertexShader=createVertexShader;t.SetPixelShader=setPixelShader;t.GetPixelShader=getPixelShader; memcpy(c->entries,&t,sizeof(t));
}
static void fillFactoryTable(FactoryContext* c) {
    IDirect3D9ExVtbl t={};t.QueryInterface=queryFactory;t.AddRef=addFactory;t.Release=releaseFactory;
    t.CreateDevice=createDevice;t.CreateDeviceEx=createDeviceEx;memcpy(c->entries,&t,sizeof(t));
}
#endif
static IDirect3D9* attachFactory(IDirect3D9* d,bool knownEx) {
    if(readConfig().bypass) { logLine("Pass-through startup: original objects returned."); return d; }
    auto c=(FactoryContext*)HeapAlloc(GetProcessHeap(),HEAP_ZERO_MEMORY,sizeof(FactoryContext));
    if(!c) return d;
    c->original=d->lpVtbl; c->real=d; c->refs=1; c->ex=knownEx;
    fillFactoryTable(c); c->lpVtbl=(const IDirect3D9Vtbl*)c->entries;
    logLine("Public factory wrapper ready; runtime untouched.");
    return (IDirect3D9*)c;
}
extern "C" IDirect3D9* WINAPI proxyCreate9(UINT version) {
    auto f=(IDirect3D9*(WINAPI*)(UINT))resolve("Direct3DCreate9");
    logLine("Direct3DCreate9: entering system runtime.");
    auto result=f?f(version):nullptr;
    logLine(result?"Direct3DCreate9: system factory returned.":"Direct3DCreate9: no factory returned."); if(result) result=attachFactory(result,false); return result;
}
extern "C" HRESULT WINAPI proxyCreate9Ex(UINT version,IDirect3D9Ex** out) {
    auto f=(HRESULT(WINAPI*)(UINT,IDirect3D9Ex**))resolve("Direct3DCreate9Ex");
    if(!f) { if(out)*out=nullptr; return E_NOTIMPL; }
    logLine("Direct3DCreate9Ex: entering system runtime.");
    HRESULT hr=f(version,out);
    logLine(SUCCEEDED(hr)?"Direct3DCreate9Ex: system factory returned.":"Direct3DCreate9Ex: system call failed."); if(SUCCEEDED(hr) && out && *out) *out=(IDirect3D9Ex*)attachFactory((IDirect3D9*)*out,true); return hr;
}
extern "C" int WINAPI proxyBegin(D3DCOLOR c,LPCWSTR n) { auto f=(int(WINAPI*)(D3DCOLOR,LPCWSTR))resolve("D3DPERF_BeginEvent");return f?f(c,n):-1; }
extern "C" int WINAPI proxyEnd() { auto f=(int(WINAPI*)())resolve("D3DPERF_EndEvent");return f?f():-1; }
extern "C" DWORD WINAPI proxyStatus() { auto f=(DWORD(WINAPI*)())resolve("D3DPERF_GetStatus");return f?f():0; }
extern "C" BOOL WINAPI proxyRepeat() { auto f=(BOOL(WINAPI*)())resolve("D3DPERF_QueryRepeatFrame");return f?f():FALSE; }
extern "C" void WINAPI proxyMarker(D3DCOLOR c,LPCWSTR n) { auto f=(void(WINAPI*)(D3DCOLOR,LPCWSTR))resolve("D3DPERF_SetMarker");if(f)f(c,n); }
extern "C" void WINAPI proxyRegion(D3DCOLOR c,LPCWSTR n) { auto f=(void(WINAPI*)(D3DCOLOR,LPCWSTR))resolve("D3DPERF_SetRegion");if(f)f(c,n); }
extern "C" void WINAPI proxyOptions(DWORD n) { auto f=(void(WINAPI*)(DWORD))resolve("D3DPERF_SetOptions");if(f)f(n); }
extern "C" void WINAPI proxyDebugSetMute() { auto f=(void(WINAPI*)())resolve("DebugSetMute");if(f)f(); }
extern "C" void WINAPI proxyDebugSetLevel(DWORD n) { auto f=(void(WINAPI*)(DWORD))resolve("DebugSetLevel");if(f)f(n); }
extern "C" void* WINAPI proxyValidator() { auto f=(void*(WINAPI*)())resolve("Direct3DShaderValidatorCreate9");return f?f():nullptr; }
extern "C" {
FARPROC rawError,rawSample;
__declspec(noreturn) void missingRaw() { logLine("Required private Direct3D export missing."); RaiseException(ERROR_PROC_NOT_FOUND,EXCEPTION_NONCONTINUABLE,0,nullptr); ExitProcess(ERROR_PROC_NOT_FOUND); }
void prepareRaw() { rawError=resolve("PSGPError");rawSample=resolve("PSGPSampleTexture");if(!rawError)rawError=(FARPROC)missingRaw;if(!rawSample)rawSample=(FARPROC)missingRaw; }
// Preserve registers, flags, FPU/SSE and the original caller stack. The exact
// private signatures are intentionally not guessed; tail-jump to the runtime.
#ifndef TEXTURELAB_NATIVE_TEST
__attribute__((naked)) void proxyError() { __asm__ volatile("pushfl\n\tpushal\n\tmovl %esp,%ebx\n\tsubl $528,%esp\n\tandl $-16,%esp\n\tfxsave (%esp)\n\tcall _prepareRaw\n\tfxrstor (%esp)\n\tmovl %ebx,%esp\n\tpopal\n\tpopfl\n\tjmp *_rawError"); }
__attribute__((naked)) void proxySample() { __asm__ volatile("pushfl\n\tpushal\n\tmovl %esp,%ebx\n\tsubl $528,%esp\n\tandl $-16,%esp\n\tfxsave (%esp)\n\tcall _prepareRaw\n\tfxrstor (%esp)\n\tmovl %ebx,%esp\n\tpopal\n\tpopfl\n\tjmp *_rawSample"); }
#endif
}
BOOL WINAPI DllMain(HINSTANCE module,DWORD reason,LPVOID) {
    if(reason==DLL_PROCESS_ATTACH) { selfModule=module; DisableThreadLibraryCalls(module); }
    return TRUE;
}
