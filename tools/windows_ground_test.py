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
ini.write_text(f'[TextureLab]\nEnabled=1\nBias=15\nMinTextureSize=32\nForceMipFilter=1\nMinMipLevel=4\nFlatGround=1\nNeutralSky={int(mode=="gray")}\n',encoding='ascii')
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
        def draw(vs,ps,sample=(32,32)):
            check(method(device,92,c.c_long,c.c_void_p)(device,vs))
            if ps is not None:check(method(device,107,c.c_long,c.c_void_p)(device,ps))
            check(method(device,43,c.c_long,w.DWORD,c.c_void_p,w.DWORD,w.DWORD,c.c_float,w.DWORD)(device,0,None,1,0xffaa1122,1,0))
            check(method(device,41,c.c_long)(device));check(method(device,83,c.c_long,w.UINT,w.UINT,c.c_void_p,w.UINT)(device,4,1,vertices,12));check(method(device,42,c.c_long)(device))
            locked=Locked();check(method(target,13,c.c_long,c.POINTER(Locked),c.c_void_p,w.DWORD)(target,c.byref(locked),None,0x10))
            try:return struct.unpack('<I',c.string_at(locked.bits+sample[1]*locked.pitch+sample[0]*4,4))[0]&0xffffff
            finally:check(method(target,14,c.c_long)(target))
        normalVS=create('struct O{float4 p:POSITION;float2 uv:TEXCOORD0;};O main(float4 p:POSITION){O o;o.p=p;o.uv=p.xy*.5+.5;return o;}','vs_2_0');normalPS=create('float4 main():COLOR {return float4(0,1,0,1);}','ps_2_0')
        assert draw(normalVS,normalPS)==0x00ff00,'Control triangle must render'
        for model in (2,3):
            grass=create(GRASS,f'vs_{model}_0');data=bytecode(grass)
            assert struct.pack('<6I',0x05000051,0xa00f0000,0,0,0xbf800000,0x3f800000) in data,'Grass replacement missing'
            assert draw(grass,normalPS)==0xaa1122,'Grass pixels should be absent'
            print('PASS: real HLSL grass recognized, replacement accepted and grass pixels absent for vs',model)
        def terrain_texture(rgb):
            texture=c.c_void_p()
            check(method(device,23,c.c_long,w.UINT,w.UINT,w.UINT,w.DWORD,w.UINT,w.UINT,c.POINTER(c.c_void_p),c.c_void_p)(device,256,256,0,0,22,1,c.byref(texture),None))
            count=method(texture,13,w.DWORD)(texture)
            for level in range(count):
                size=max(1,256>>level);locked=Locked()
                check(method(texture,19,c.c_long,w.UINT,c.POINTER(Locked),c.c_void_p,w.DWORD)(texture,level,c.byref(locked),None,0))
                try:
                    for y in range(size):
                        row=[]
                        for x in range(size):
                            # Original detailed levels have checker contrast; low mip
                            # levels preserve the material's average natural color.
                            scale=1 if level>=4 else (.5 if (x+y)%2 else 1.5)
                            r,g,b=[min(255,round(v*scale)) for v in rgb]
                            row.append(0xff000000|(r<<16)|(g<<8)|b)
                        c.memmove(locked.bits+y*locked.pitch,struct.pack('<'+'I'*size,*row),size*4)
                finally:check(method(texture,20,c.c_long,w.UINT)(texture,level))
            return texture
        for model in (2,3):
            ground=create(GROUND,f'ps_{model}_0');data=bytecode(ground)
            if mode=='gray':
                assert struct.pack('<3I',0x3e8f5c29,0x3eae147b,0x3e4ccccd) in data,'Dark ground replacement missing'
            else:
                assert data==bytes(compile(GROUND,f'ps_{model}_0')),'Normal sky must preserve terrain material shader'
            for natural in ((102,132,62),(145,111,71)):
                texture=terrain_texture(natural)
                try:
                    check(method(device,65,c.c_long,w.DWORD,c.c_void_p)(device,0,texture))
                    pixel=draw(normalVS,ground);rgb=((pixel>>16)&255,(pixel>>8)&255,pixel&255)
                    expected=(71,87,51) if mode=='gray' else natural
                    assert all(abs(a-b)<=2 for a,b in zip(rgb,expected)),f'Unexpected {mode} terrain: {rgb}, expected {expected}'
                finally:
                    check(method(device,65,c.c_long,w.DWORD,c.c_void_p)(device,0,None));release(texture)
            print('PASS:',mode,'terrain preserves natural green/brown colors with low mip detail' if mode=='normal' else 'terrain retains dark flat palette','for ps',model)

        # Foliage regression: mip 0 contains a visible cut-out leaf; all lower
        # mips are transparent. An imposed bias/mip floor would erase the leaf.
        for fmt,label in ((21,'RGBA'),(0x31545844,'DXT1'),(0x35545844,'DXT5')):
            leaf=c.c_void_p()
            hr=method(device,23,c.c_long,w.UINT,w.UINT,w.UINT,w.DWORD,w.UINT,w.UINT,c.POINTER(c.c_void_p),c.c_void_p)(device,256,256,0,0,fmt,1,c.byref(leaf),None)
            if hr<0 and fmt!=21:
                print('SKIP: driver cannot create foliage fixture',label);continue
            check(hr)
            try:
                count=method(leaf,13,w.DWORD)(leaf)
                for level in range(count):
                    size=max(1,256>>level);locked=Locked()
                    check(method(leaf,19,c.c_long,w.UINT,c.POINTER(Locked),c.c_void_p,w.DWORD)(leaf,level,c.byref(locked),None,0))
                    try:
                        if fmt==21:
                            for y in range(size):
                                row=[(0xff00ff00 if level==0 and 64<=x<192 and 64<=y<192 else 0x0000ff00) for x in range(size)]
                                c.memmove(locked.bits+y*locked.pitch,struct.pack('<'+'I'*size,*row),size*4)
                        else:
                            blocks=max(1,(size+3)//4)
                            for y in range(blocks):
                                row=b''
                                for x in range(blocks):
                                    solid=level==0 and 64<=x*4<192 and 64<=y*4<192
                                    if fmt==0x31545844:
                                        row+=struct.pack('<HHI',0x07e0,0x07e0,0 if solid else 0xffffffff)
                                    else:
                                        indices=0 if solid else sum(1<<(3*j) for j in range(16))
                                        row+=bytes((255,0))+indices.to_bytes(6,'little')+struct.pack('<HHI',0x07e0,0x07e0,0)
                                c.memmove(locked.bits+y*locked.pitch,row,len(row))
                    finally:check(method(leaf,20,c.c_long,w.UINT)(leaf,level))
                check(method(device,65,c.c_long,w.DWORD,c.c_void_p)(device,0,leaf))
                getstate=method(device,68,c.c_long,w.DWORD,w.UINT,c.POINTER(w.DWORD))
                setstate=method(device,69,c.c_long,w.DWORD,w.UINT,w.DWORD)
                for state in (7,8,9):
                    check(setstate(device,0,state,0));value=w.DWORD();check(getstate(device,0,state,c.byref(value)))
                    # Coverage is restored at the draw, after shader/state changes.
                source='sampler2D sam_diffuse:register(s0);float4 main(float2 uv:TEXCOORD0):COLOR {float4 leaf=tex2D(sam_diffuse,uv);clip(leaf.a-.5);return leaf;}'
                for model in (2,3):
                    shader=create(source,f'ps_{model}_0')
                    assert draw(normalVS,shader)==0x00ff00,(label,model,'leaf disappeared')
                    assert draw(normalVS,shader,(32,54))==0xaa1122,(label,model,'leaf cutout lost')
                    for state in (7,8,9):
                        value=w.DWORD();check(getstate(device,0,state,c.byref(value)))
                        assert value.value==0,(label,model,state,value.value)
                    # Same RGBA/DXT resource is reduced again with an opaque
                    # shader: no blanket format exclusion may remain.
                    assert draw(normalVS,normalPS)==0x00ff00
                    value=w.DWORD();check(getstate(device,0,8,c.byref(value)))
                    assert struct.unpack('<f',struct.pack('<I',value.value))[0]==15.0,(label,'opaque bias missing')
                    check(getstate(device,0,9,c.byref(value)));assert value.value==4,(label,'opaque mip floor missing')
                    assert draw(normalVS,shader)==0x00ff00,(label,'leaf lost after opaque draw')
                    native=c.c_void_p();block=c.c_void_p()
                    try:
                        check(method(leaf,3,c.c_long,c.POINTER(c.c_void_p))(leaf,c.byref(native)))
                        check(method(device,59,c.c_long,w.UINT,c.POINTER(c.c_void_p))(device,1,c.byref(block)))
                        assert draw(normalVS,normalPS)==0x00ff00
                        check(method(native,107,c.c_long,c.c_void_p)(native,shader))
                        assert draw(normalVS,None)==0x00ff00,(label,'native shader bind lost leaves')
                        assert draw(normalVS,normalPS)==0x00ff00
                        check(method(block,5,c.c_long)(block))
                        assert draw(normalVS,None)==0x00ff00,(label,'state-block shader bind lost leaves')
                    finally:release(block);release(native)
                    print('PASS: original leaf pixels and cutout retained with aggressive mip settings',mode,label,model)
            finally:
                check(method(device,65,c.c_long,w.DWORD,c.c_void_p)(device,0,None));release(leaf)

finally:
    for shader in shaders:release(shader)
    release(target);release(device);release(factory)
    if window:user.DestroyWindow(window)
    ini.unlink(missing_ok=True)
