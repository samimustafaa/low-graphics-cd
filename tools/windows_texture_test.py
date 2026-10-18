"""Check actual sampler state through D3D9 when the runner can create a device."""
import ctypes as c
from ctypes import wintypes as w
from pathlib import Path
import struct

class Present(c.Structure):
    _fields_ = [(n,t) for n,t in [('width',w.UINT),('height',w.UINT),('format',w.UINT),('count',w.UINT),('samples',w.UINT),('quality',w.DWORD),('swap',w.UINT),('window',w.HWND),('windowed',w.BOOL),('depth',w.BOOL),('depth_format',w.UINT),('flags',w.DWORD),('refresh',w.UINT),('interval',w.UINT)]]

def method(obj, slot, result, *args):
    table=c.cast(obj,c.POINTER(c.POINTER(c.c_void_p))).contents
    return c.WINFUNCTYPE(result,c.c_void_p,*args)(table[slot])

def release(obj):
    if obj: method(obj,2,w.ULONG)(obj)

def check(hr):
    assert hr>=0, f'D3D9 failure: {hr & 0xffffffff:08x}'

ini=Path('CD_TextureLab.ini')
assert not ini.exists(), 'Test needs a clean source/build directory'
ini.write_text('[TextureLab]\nEnabled=1\nBias=15\nMinTextureSize=32\nForceMipFilter=1\nIncludeAutogen=1\nNeutralSky=0\n',encoding='ascii')
user=c.WinDLL('user32')
user.CreateWindowExW.argtypes=[w.DWORD,w.LPCWSTR,w.LPCWSTR,w.DWORD,c.c_int,c.c_int,c.c_int,c.c_int,w.HWND,c.c_void_p,c.c_void_p,c.c_void_p]
user.CreateWindowExW.restype=w.HWND
user.DestroyWindow.argtypes=[w.HWND]
window=user.CreateWindowExW(0,'STATIC','Texture Lab test',0x80000000,0,0,64,64,None,None,None,None)
factory=device=texture=None
try:
    dll=c.WinDLL(str(Path('d3d9.dll').resolve()))
    dll.Direct3DCreate9.argtypes=[w.UINT];dll.Direct3DCreate9.restype=c.c_void_p
    factory=dll.Direct3DCreate9(32);assert factory
    params=Present();params.width=params.height=64;params.count=1;params.swap=1;params.window=window;params.windowed=1;params.interval=0x80000000
    device=c.c_void_p()
    hr=method(factory,16,c.c_long,w.UINT,w.UINT,w.HWND,w.DWORD,c.POINTER(Present),c.POINTER(c.c_void_p))(factory,0,1,window,0x20,c.byref(params),c.byref(device))
    if hr<0:
        print(f'SKIP: runner has no usable D3D9 device ({hr & 0xffffffff:08x}); simulated sampler tests remain required')
    else:
        setstate=method(device,69,c.c_long,w.DWORD,w.UINT,w.DWORD)
        getstate=method(device,68,c.c_long,w.DWORD,w.UINT,c.POINTER(w.DWORD))
        bind=method(device,65,c.c_long,w.DWORD,c.c_void_p)
        create=method(device,23,c.c_long,w.UINT,w.UINT,w.UINT,w.DWORD,w.UINT,w.UINT,c.POINTER(c.c_void_p),c.c_void_p)
        texture=c.c_void_p();check(create(device,256,256,0,0,21,1,c.byref(texture),None))
        check(setstate(device,0,7,0));check(setstate(device,0,8,0))
        check(bind(device,0,texture))
        # Reproduce the previously missed call order: game writes after binding.
        check(setstate(device,0,8,0));check(setstate(device,0,7,0))
        bias=w.DWORD();filt=w.DWORD();check(getstate(device,0,8,c.byref(bias)));check(getstate(device,0,7,c.byref(filt)))
        assert struct.unpack('<f',struct.pack('<I',bias.value))[0]==15.0
        assert filt.value==1
        check(bind(device,0,None))
        check(getstate(device,0,8,c.byref(bias)));check(getstate(device,0,7,c.byref(filt)))
        assert bias.value==0 and filt.value==0
        print('PASS: real D3D9 texture bind, late sampler writes, effective bias/filter, and restoration on unbind')
finally:
    release(texture);release(device);release(factory)
    if window:user.DestroyWindow(window)
    ini.unlink(missing_ok=True)
