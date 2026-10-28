"""Render classic/new sky shaders through the actual proxy in Gray, Black and Off sessions."""
import ctypes as c
from ctypes import wintypes as w
from pathlib import Path
import struct
import sys, subprocess
if len(sys.argv)==1:
    for mode in ('gray','black','off','opaque','opaque_off'):
        subprocess.run([sys.executable,__file__,mode],check=True)
    raise SystemExit(0)
mode=sys.argv[1]
assert mode in ('gray','black','off','opaque','opaque_off')
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

SKIES=[
    'float4 skycolormid;float4 skycolorlow;float4 u_bg_color;float4 main():COLOR {return float4(0,0,1,1)+(skycolormid+skycolorlow+u_bg_color)*0.00001;}',
    'float4 skycolormid;float4 skycolorhigh;float4 bk_cloud_color;float cloud_thickness;float4 main():COLOR {return float4(0,0,1,1)+(skycolormid+skycolorhigh+bk_cloud_color+cloud_thickness)*0.00001;}'
]
ini=Path('CD_TextureLab.ini');assert not ini.exists()
ini.write_text(f'[TextureLab]\nEnabled=1\nBias=0\nFlatGround=0\nNeutralSky={int(mode in ("gray","black"))}\nBlackSky={int(mode=="black")}\nOpaqueStructures={int(mode=="opaque")}\n',encoding='ascii')
user=c.WinDLL('user32');user.CreateWindowExW.argtypes=[w.DWORD,w.LPCWSTR,w.LPCWSTR,w.DWORD,c.c_int,c.c_int,c.c_int,c.c_int,w.HWND,c.c_void_p,c.c_void_p,c.c_void_p];user.CreateWindowExW.restype=w.HWND;user.DestroyWindow.argtypes=[w.HWND]
window=user.CreateWindowExW(0,'STATIC','Sky color test',0x80000000,0,0,64,64,None,None,None,None)
factory=device=target=resource=native_device=None;shaders=[]
try:
    dll=c.WinDLL(str(Path('d3d9.dll').resolve()));dll.Direct3DCreate9.argtypes=[w.UINT];dll.Direct3DCreate9.restype=c.c_void_p
    factory=dll.Direct3DCreate9(32);assert factory
    params=Present();params.width=params.height=64;params.count=1;params.swap=1;params.window=window;params.windowed=1;params.interval=0x80000000
    device=c.c_void_p();hr=method(factory,16,c.c_long,w.UINT,w.UINT,w.HWND,w.DWORD,c.POINTER(Present),c.POINTER(c.c_void_p))(factory,0,1,window,0x20,c.byref(params),c.byref(device))
    if hr<0:print(f'SKIP: no D3D9 device ({hr & 0xffffffff:08x}); native sky tests remain required')
    else:
        resource=c.c_void_p()
        check(method(device,23,c.c_long,w.UINT,w.UINT,w.UINT,w.DWORD,w.UINT,w.UINT,c.POINTER(c.c_void_p),c.c_void_p)(device,16,16,1,0,21,1,c.byref(resource),None))
        native_device=c.c_void_p()
        check(method(resource,3,c.c_long,c.POINTER(c.c_void_p))(resource,c.byref(native_device)))
        assert native_device.value!=device.value,'Resource GetDevice must expose the native creation path'
        def create(source,profile,direct=False):
            data=compile(source,profile);shader=c.c_void_p();slot=91 if profile.startswith('vs') else 106
            owner=native_device if direct else device
            check(method(owner,slot,c.c_long,c.c_void_p,c.POINTER(c.c_void_p))(owner,data,c.byref(shader)));shaders.append(shader);return shader
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
        # Ordinary ground with sky-like names must retain its green output.
        floor=create('float4 sky_color;float4 safe_range_color;float4 main():COLOR {return float4(0,1,0,1)+(sky_color+safe_range_color)*0.00001;}','ps_2_0',True)
        assert draw(normalVS,floor)==0x00ff00,'Sky mode changed ordinary ground/floor output'
        print('PASS: sky mode leaves ground/floor colors unchanged',mode)
        for direct in (False,True):
            for model in (2,3):
                for variant,source in zip(('classic','new'),SKIES):
                    sky=create(source,f'ps_{model}_0',direct)
                    pixel=draw(normalVS,sky)
                    logical=c.c_void_p();check(method(device,108,c.c_long,c.POINTER(c.c_void_p))(device,c.byref(logical)))
                    assert logical.value==sky.value,'GetPixelShader changed logical shader identity';release(logical)
                    actual_shader=c.c_void_p();check(method(native_device,108,c.c_long,c.POINTER(c.c_void_p))(native_device,c.byref(actual_shader)))
                    try:data=bytecode(actual_shader)
                    finally:release(actual_shader)
                    if mode in ('gray','black'):
                        rgb=0 if mode=='black' else 0x3f000000
                        expected=struct.pack('<6I',0x05000051,0xa00f0000,rgb,rgb,rgb,0x3f800000)
                        assert expected in data,f'{variant} sky did not receive {mode} replacement'
                    expected=0x000000 if mode=='black' else (0x808080 if mode=='gray' else 0x0000ff)
                    actual=((pixel>>16)&255,(pixel>>8)&255,pixel&255)
                    expected_rgb=((expected>>16)&255,(expected>>8)&255,expected&255)
                    assert all(abs(a-b)<=1 for a,b in zip(actual,expected_rgb)),f'{variant} ps{model} {mode}: actual {actual}, expected {expected_rgb}'
                    print('PASS: real SKY pixels',variant,'ps',model,mode,'native-created' if direct else 'wrapper-created',actual)

        # Actual D3DCompile + blended pixels: structure alpha changes, RGB and
        # unrelated translucent materials remain untouched, on both creation paths.
        if mode in ('opaque','opaque_off'):
            names=('dismantling_scale','rongjie_fazhi','rongjiezhi','alpha_intensty','AlphaMtl','diffuse_instensty')
            source=';'.join('float '+n for n in names)+'; sampler2D sam_other0;'
            source+='float4 main():COLOR {return float4(.25,.5,.75,.25)+('
            source+='+'.join(names)+'+tex2D(sam_other0,float2(.5,.5)).x)*0.000001;}'
            unrelated='float4 main():COLOR {return float4(.25,.5,.75,.25);}'
            for state,value in [(27,1),(19,5),(20,6)]:
                check(method(device,57,c.c_long,w.UINT,w.DWORD)(device,state,value))
            for direct in (False,True):
                for model in (2,3):
                    for selected,text in ((False,unrelated),(True,source)):
                        ps=create(text,f'ps_{model}_0',direct)
                        pixel=draw(normalVS,ps)
                        rgb=((pixel>>16)&255,(pixel>>8)&255,pixel&255)
                        expected=(64,128,191) if selected and mode=='opaque' else (144,45,73)
                        assert all(abs(a-b)<=2 for a,b in zip(rgb,expected)),(mode,selected,direct,model,rgb,expected)
                        logical=c.c_void_p();check(method(device,108,c.c_long,c.POINTER(c.c_void_p))(device,c.byref(logical)))
                        assert logical.value==ps.value;release(logical)
                        print('PASS: real structure opacity pixels',mode,selected,direct,model,rgb)

finally:
    for shader in shaders:release(shader)
    release(target);release(resource);release(native_device);release(device);release(factory)
    if window:user.DestroyWindow(window)
    ini.unlink(missing_ok=True)
