// Portable Win32/COM test doubles. Not compiled into the shipping DLL.
#pragma once
#include <cstdint>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <cwchar>
#include <string>
#include <map>
#include <chrono>
#define WINAPI
#define STDMETHODCALLTYPE
#define CALLBACK
#define __declspec(x)
using DWORD=std::uint32_t;using ULONG=std::uint32_t;using LONG=std::int32_t;
using UINT=unsigned;using HRESULT=std::int32_t;using BOOL=int;using ULONGLONG=std::uint64_t;
using HMODULE=void*;using HANDLE=void*;using HWND=void*;using HINSTANCE=void*;
using PVOID=void*;using LPVOID=void*;using LPCWSTR=const wchar_t*;using FARPROC=void(*)();
using REFIID=int;using D3DCOLOR=DWORD;using D3DDEVTYPE=int;using D3DRESOURCETYPE=int;using D3DSAMPLERSTATETYPE=int;
constexpr HRESULT S_OK=0,E_NOINTERFACE=-1,E_NOTIMPL=-2,D3DERR_DEVICELOST=-3,E_POINTER=-4,D3DERR_INVALIDCALL=-5;
#define SUCCEEDED(x) ((x)>=0)
#define FAILED(x) ((x)<0)
constexpr int TRUE=1,FALSE=0,MAX_PATH=260;
constexpr DWORD FILE_APPEND_DATA=1,FILE_SHARE_READ=1,FILE_SHARE_WRITE=2,OPEN_ALWAYS=1,FILE_ATTRIBUTE_NORMAL=0;
constexpr DWORD HEAP_ZERO_MEMORY=1,TLS_OUT_OF_INDEXES=0xffffffff,GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS=4,GET_MODULE_HANDLE_EX_FLAG_PIN=1;
constexpr DWORD ERROR_PROC_NOT_FOUND=127,EXCEPTION_NONCONTINUABLE=1,DLL_PROCESS_ATTACH=1;
#define INVALID_HANDLE_VALUE ((HANDLE)(std::intptr_t)-1)
constexpr int D3DRTYPE_TEXTURE=3,D3DSAMP_MIPMAPLODBIAS=8;
constexpr DWORD D3DUSAGE_RENDERTARGET=1,D3DUSAGE_DEPTHSTENCIL=2,D3DUSAGE_AUTOGENMIPMAP=1024;
constexpr int IID_IDirect3DDevice9Ex=1,IID_IDirect3D9Ex=2,IID_IUnknown=3,IID_IDirect3DDevice9=4,IID_IDirect3D9=5;
inline bool IsEqualIID(REFIID a,REFIID b){return a==b;}
struct INIT_ONCE {bool ran;};using PINIT_ONCE=INIT_ONCE*;
#define INIT_ONCE_STATIC_INIT {false}
struct D3DPRESENT_PARAMETERS {};struct D3DDISPLAYMODEEX {};struct IDirect3DStateBlock9 {};
struct D3DSURFACE_DESC {DWORD Usage,Width,Height;};
struct IDirect3DPixelShader9;
struct IDirect3DDevice9;struct IDirect3DDevice9Ex;struct IDirect3D9;struct IDirect3D9Ex;struct IDirect3DTexture9;
using IDirect3DBaseTexture9=IDirect3DTexture9;
#define DEVICE_PREFIX \
 HRESULT(*QueryInterface)(IDirect3DDevice9*,REFIID,void**); \
 ULONG(*AddRef)(IDirect3DDevice9*); \
 ULONG(*Release)(IDirect3DDevice9*); \
 HRESULT(*SetTexture)(IDirect3DDevice9*,DWORD,IDirect3DBaseTexture9*); \
 HRESULT(*SetSamplerState)(IDirect3DDevice9*,DWORD,D3DSAMPLERSTATETYPE,DWORD); \
 HRESULT(*Reset)(IDirect3DDevice9*,D3DPRESENT_PARAMETERS*); \
 HRESULT(*BeginStateBlock)(IDirect3DDevice9*); \
 HRESULT(*EndStateBlock)(IDirect3DDevice9*,IDirect3DStateBlock9**); \
 HRESULT(*CreatePixelShader)(IDirect3DDevice9*,const DWORD*,IDirect3DPixelShader9**)
struct IDirect3DDevice9Vtbl {DEVICE_PREFIX;};
struct IDirect3DDevice9ExVtbl {DEVICE_PREFIX;HRESULT(*ResetEx)(IDirect3DDevice9Ex*,D3DPRESENT_PARAMETERS*,D3DDISPLAYMODEEX*);};
struct IDirect3DDevice9 {const IDirect3DDevice9Vtbl*lpVtbl;};
struct IDirect3DDevice9Ex {const IDirect3DDevice9ExVtbl*lpVtbl;};
#define FACTORY_PREFIX \
 HRESULT(*QueryInterface)(IDirect3D9*,REFIID,void**); \
 ULONG(*AddRef)(IDirect3D9*); \
 ULONG(*Release)(IDirect3D9*); \
 HRESULT(*CreateDevice)(IDirect3D9*,UINT,D3DDEVTYPE,HWND,DWORD,D3DPRESENT_PARAMETERS*,IDirect3DDevice9**)
struct IDirect3D9Vtbl {FACTORY_PREFIX;};
struct IDirect3D9ExVtbl {FACTORY_PREFIX;HRESULT(*CreateDeviceEx)(IDirect3D9Ex*,UINT,D3DDEVTYPE,HWND,DWORD,D3DPRESENT_PARAMETERS*,D3DDISPLAYMODEEX*,IDirect3DDevice9Ex**);};
struct IDirect3D9 {const IDirect3D9Vtbl*lpVtbl;};struct IDirect3D9Ex {const IDirect3D9ExVtbl*lpVtbl;};
struct IDirect3DPixelShader9Vtbl {ULONG(*Release)(IDirect3DPixelShader9*);HRESULT(*GetFunction)(IDirect3DPixelShader9*,void*,UINT*);};
struct IDirect3DPixelShader9 {const IDirect3DPixelShader9Vtbl*lpVtbl;};
#define IDirect3DPixelShader9_GetFunction(s,p,n) ((s)->lpVtbl->GetFunction(s,p,n))
#define IDirect3DPixelShader9_Release(s) ((s)->lpVtbl->Release(s))
struct IDirect3DTexture9Vtbl {D3DRESOURCETYPE(*GetType)(IDirect3DTexture9*);DWORD(*GetLevelCount)(IDirect3DTexture9*);HRESULT(*GetLevelDesc)(IDirect3DTexture9*,UINT,D3DSURFACE_DESC*);};
struct IDirect3DTexture9 {const IDirect3DTexture9Vtbl*lpVtbl;};
#define IDirect3DDevice9_SetTexture(d,a,b) ((d)->lpVtbl->SetTexture(d,a,b))
#define IDirect3DDevice9_SetSamplerState(d,a,b,c) ((d)->lpVtbl->SetSamplerState(d,a,b,c))
#define IDirect3DDevice9_Reset(d,p) ((d)->lpVtbl->Reset(d,p))
#define IDirect3DDevice9_Release(d) ((d)->lpVtbl->Release(d))
#define IDirect3DDevice9_BeginStateBlock(d) ((d)->lpVtbl->BeginStateBlock(d))
#define IDirect3DDevice9_EndStateBlock(d,p) ((d)->lpVtbl->EndStateBlock(d,p))
#define IDirect3DDevice9Ex_Release(d) ((d)->lpVtbl->Release((IDirect3DDevice9*)d))
#define IDirect3D9Ex_Release(d) ((d)->lpVtbl->Release((IDirect3D9*)d))
#define IDirect3DBaseTexture9_GetType(t) ((t)->lpVtbl->GetType(t))
#define IDirect3DBaseTexture9_GetLevelCount(t) ((t)->lpVtbl->GetLevelCount(t))
#define IDirect3DTexture9_GetLevelDesc(t,l,o) ((t)->lpVtbl->GetLevelDesc(t,l,o))
inline thread_local void* threadValue=nullptr;
inline LONG InterlockedIncrement(volatile LONG*p){return __atomic_add_fetch(p,1,__ATOMIC_SEQ_CST);}
inline LONG InterlockedDecrement(volatile LONG*p){return __atomic_sub_fetch(p,1,__ATOMIC_SEQ_CST);}
inline LONG InterlockedExchange(volatile LONG*p,LONG value){return __atomic_exchange_n(p,value,__ATOMIC_SEQ_CST);}
inline LONG InterlockedCompareExchange(volatile LONG*p,LONG value,LONG compare){__atomic_compare_exchange_n(p,&compare,value,false,__ATOMIC_SEQ_CST,__ATOMIC_SEQ_CST);return compare;}
inline PVOID InterlockedExchangePointer(PVOID volatile*p,PVOID value){return __atomic_exchange_n(p,value,__ATOMIC_SEQ_CST);}
inline DWORD TlsAlloc(){return 0;}inline void*TlsGetValue(DWORD){return threadValue;}
inline BOOL TlsSetValue(DWORD,void*v){threadValue=v;return TRUE;}inline BOOL TlsFree(DWORD){return TRUE;}
inline HANDLE GetProcessHeap(){return (HANDLE)1;}
inline int contextAllocations=0;
inline void*HeapAlloc(HANDLE,DWORD,std::size_t n){++contextAllocations;return std::calloc(1,n);}
inline BOOL HeapFree(HANDLE,DWORD,void*p){--contextAllocations;std::free(p);return TRUE;}
constexpr DWORD MEM_COMMIT=4096,PAGE_NOACCESS=1,PAGE_GUARD=256;
struct MEMORY_BASIC_INFORMATION {void*BaseAddress;std::size_t RegionSize;DWORD State,Protect;};
inline std::size_t VirtualQuery(const void*,MEMORY_BASIC_INFORMATION*,std::size_t){return 0;}
inline thread_local DWORD mockThreadId=1;
inline DWORD GetCurrentProcessId(){return 1;}inline DWORD GetCurrentThreadId(){return mockThreadId;}
inline ULONGLONG GetTickCount64(){return(std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now().time_since_epoch()).count());}
inline std::map<std::wstring,std::wstring> profile;
inline BOOL WritePrivateProfileStringW(LPCWSTR,LPCWSTR key,LPCWSTR value,LPCWSTR){profile[key]=value;return TRUE;}
inline UINT GetPrivateProfileIntW(LPCWSTR,LPCWSTR key,int fallback,LPCWSTR){auto p=profile.find(key);return p==profile.end()?fallback:std::stoi(p->second);}
inline DWORD GetTempPathW(DWORD,wchar_t*out){std::wcscpy(out,L"/tmp/");return 5;}
inline std::string narrow(LPCWSTR p){std::wstring s(p);return std::string(s.begin(),s.end());}
inline HANDLE CreateFileW(LPCWSTR path,DWORD,DWORD,void*,DWORD,DWORD,void*){auto f=std::fopen(narrow(path).c_str(),"ab");return f?(HANDLE)f:INVALID_HANDLE_VALUE;}
inline BOOL WriteFile(HANDLE f,const void*data,DWORD n,DWORD*out,void*){*out=std::fwrite(data,1,n,(FILE*)f);return TRUE;}
inline BOOL CloseHandle(HANDLE f){std::fclose((FILE*)f);return TRUE;}
inline BOOL DeleteFileW(LPCWSTR p){std::remove(narrow(p).c_str());return TRUE;}
inline UINT GetSystemDirectoryW(wchar_t*,UINT){return 0;}
inline HMODULE LoadLibraryW(LPCWSTR){return nullptr;}
inline DWORD GetModuleFileNameW(HMODULE,wchar_t*,DWORD){return 0;}
inline BOOL GetModuleHandleExW(DWORD,LPCWSTR,HMODULE*out){*out=nullptr;return TRUE;}
inline FARPROC GetProcAddress(HMODULE,const char*){return nullptr;}
inline BOOL InitOnceExecuteOnce(PINIT_ONCE once,BOOL(*callback)(PINIT_ONCE,PVOID,PVOID*),PVOID param,PVOID*out){if(!once->ran){once->ran=true;return callback(once,param,out);}return TRUE;}
inline BOOL DisableThreadLibraryCalls(HMODULE){return TRUE;}
inline void RaiseException(DWORD,DWORD,DWORD,const void*){std::abort();}
[[noreturn]] inline void ExitProcess(UINT value){std::exit(value);}
