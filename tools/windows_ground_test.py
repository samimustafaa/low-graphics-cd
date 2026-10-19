"""Check real HLSL recognition, absent grass and flat terrain pixels through D3D9."""
import ctypes as c
from ctypes import wintypes as w
from pathlib import Path
import struct
import sys
from windows_texture_test import Present, method, release, check
compiler=c.WinDLL('d3dcompiler_47.dll');compile_shader=compiler.D3DCompile
compile_shader.argtypes=[c.c_void_p,c.c_size_t,c.c_char_p,c.c_void_p,c.c_void_p,c.c_char_p,c.c_char_p,w.UINT,w.UINT,c.POINTER(c.c_void_p),c.POINTER(c.c_void_p)];compile_shader.restype=c.c_long

def compile(source,profile):
    source=source.encode();blob=c.c_void_p();errors=c.c_void_p()
    hr=compile_shader(source,len(source),None,None,None,b'main',profile.encode(),4,0,c.byref(blob),c.byref(errors))
    try:
        if hr<0:
            address=method(errors,3,c.c_void_p)(errors) if errors else None
            raise AssertionError(c.string_at(address).decode() if address else f'Compile failed {hr}')
        size=method(blob,4,c.c_size_t)(blob);address=method(blob,3,c.c_void_p)(blob)
        return (w.DWORD*(size//4)).from_buffer_copy(c.string_at(address,size))
    finally:release(blob);release(errors)

GRASS='''float4 WindInfo; float u_visible_dist; float4 char_pos; float4x4 u_wvp;
float4 main(float4 p:POSITION):POSITION {return mul(p,u_wvp)+float4(WindInfo.x,u_visible_dist,char_pos.x,0)*0.00001;}'''
GROUND='''float4 safe_range_color;float4 char_pos;float4 sky_color;float4 weather_intensity;sampler2D sam_other0:register(s0);
float4 main(float2 uv:TEXCOORD0):COLOR {return tex2D(sam_other0,uv)+(safe_range_color+char_pos+sky_color+weather_intensity)*0.00001;}'''
ini=Path('CD_TextureLab.ini');assert not ini.exists()
mode=sys.argv[1] if len(sys.argv)>1 else 'normal'
assert mode in ('normal','gray')
ini.write_text(f'[TextureLab]\nEnabled=1\nBias=0\nFlatGround=1\nNeutralSky={int(mode=="gray")}\n',encoding='ascii')
user=c.WinDLL('user32');user.CreateWindowExW.argtypes=[w.DWORD,w.LPCWSTR,w.LPCWSTR,w.DWORD,c.c_int,c.c_int,c.c_int,c.c_int,w.HWND,c.c_void_p,c.c_void_p,c.c_void_p];user.CreateWindowExW.restype=w.HWND;user.DestroyWindow.argtypes=[w.HWND]
window=user.CreateWindowExW(0,'STATIC','Ground shader test',0x80000000,0,0,64,64,None,None,None,None)
factory=device=target=None;shaders=[]
try:
    dll=c.WinDLL(str(Path('d3d9.dll').resolve()));dll.Direct3DCreate9.argtypes=[w.UINT];dll.Direct3DCreate9.restype=c.c_void_p
    factory=dll.Direct3DCreate9(32);assert factory
    params=Present();params.width=params.height=64;params.count=1;params.swap=1;params.window=window;params.windowed=1;params.interval=0x80000000
    device=c.c_void_p();hr=method(factory,16,c.c_long,w.UINT,w.UINT,w.HWND,w.DWORD,c.POINTER(Present),c.POINTER(c.c_void_p))(factory,0,1,window,0x20,c.byref(params),c.byref(device))
    if hr<0:print(f'SKIP: no D3D9 device ({hr & 0xffffffff:08x}); native grass/terrain tests remain required')
    else:
        def create(source,profile):
            data=compile(source,profile);shader=c.c_void_p();slot=91 if profile.startswith('vs') else 106
            check(method(device,slot,c.c_long,c.c_void_p,c.POINTER(c.c_void_p))(device,data,c.byref(shader)));shaders.append(shader);return shader
        def bytecode(shader):
            size=w.UINT();fn=method(shader,4,c.c_long,c.c_void_p,c.POINTER(w.UINT));check(fn(shader,None,c.byref(size)))
            data=(w.DWORD*(size.value//4))();check(fn(shader,data,c.byref(size)));return bytes(data)
        target=c.c_void_p();check(method(device,28,c.c_long,w.UINT,w.UINT,w.UINT,w.UINT,w.DWORD,w.BOOL,c.POINTER(c.c_void_p),c.c_void_p)(device,64,64,21,0,0,True,c.byref(target),None))
        check(method(device,37,c.c_long,w.DWORD,c.c_void_p)(device,0,target))
        for state,value in [(7,0),(22,1),(27,0),(15,0)]:check(method(device,57,c.c_long,w.UINT,w.DWORD)(device,state,value))
        check(method(device,89,c.c_long,w.DWORD)(device,0x002))
        vertices=(c.c_float*9)(-1,-1,.5, 0,1,.5, 1,-1,.5)
        class Locked(c.Structure):_fields_=[('pitch',c.c_int),('bits',c.c_void_p)]
        def draw(vs,ps):
            check(method(device,92,c.c_long,c.c_void_p)(device,vs));check(method(device,107,c.c_long,c.c_void_p)(device,ps))
            check(method(device,43,c.c_long,w.DWORD,c.c_void_p,w.DWORD,w.DWORD,c.c_float,w.DWORD)(device,0,None,1,0xffaa1122,1,0))
            check(method(device,41,c.c_long)(device));check(method(device,83,c.c_long,w.UINT,w.UINT,c.c_void_p,w.UINT)(device,4,1,vertices,12));check(method(device,42,c.c_long)(device))
            locked=Locked();check(method(target,13,c.c_long,c.POINTER(Locked),c.c_void_p,w.DWORD)(target,c.byref(locked),None,0x10))
            try:return struct.unpack('<I',c.string_at(locked.bits+32*locked.pitch+32*4,4))[0]&0xffffff
            finally:check(method(target,14,c.c_long)(target))
        normalVS=create('float4 main(float4 p:POSITION):POSITION {return p;}','vs_2_0');normalPS=create('float4 main():COLOR {return float4(0,1,0,1);}','ps_2_0')
        assert draw(normalVS,normalPS)==0x00ff00,'Control triangle must render'
        for model in (2,3):
            grass=create(GRASS,f'vs_{model}_0');data=bytecode(grass)
            assert struct.pack('<6I',0x05000051,0xa00f0000,0,0,0xbf800000,0x3f800000) in data,'Grass replacement missing'
            assert draw(grass,normalPS)==0xaa1122,'Grass pixels should be absent'
            print('PASS: real HLSL grass recognized, replacement accepted and grass pixels absent for vs',model)
        for model in (2,3):
            ground=create(GROUND,f'ps_{model}_0');data=bytecode(ground)
            constants=(0x3e8f5c29,0x3eae147b,0x3e4ccccd) if mode=='gray' else (0x3f3851ec,0x3f3d70a4,0x3f333333)
            assert struct.pack('<3I',*constants) in data,'Flat ground replacement missing'
            pixel=draw(normalVS,ground);rgb=((pixel>>16)&255,(pixel>>8)&255,pixel&255)
            expected=(71,87,51) if mode=='gray' else (184,189,178)
            assert all(abs(a-b)<=2 for a,b in zip(rgb,expected)),f'Unexpected {mode} ground color {rgb}'
            print('PASS: real HLSL terrain recognized and',mode,'ground pixels rendered for ps',model)
finally:
    for shader in shaders:release(shader)
    release(target);release(device);release(factory)
    if window:user.DestroyWindow(window)
    ini.unlink(missing_ok=True)
