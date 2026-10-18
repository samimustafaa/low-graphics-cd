"""Real Windows DLL/factory loading and independent shader-token assembly checks."""
import ctypes as c
from ctypes import wintypes as w
from pathlib import Path
import struct

assert c.sizeof(c.c_void_p) == 4, 'Run this test with 32-bit Python'
runtime = c.WinDLL(str(Path('d3d9.dll').resolve()))
runtime.Direct3DCreate9.argtypes = [w.UINT]
runtime.Direct3DCreate9.restype = c.c_void_p
factory = runtime.Direct3DCreate9(32)
assert factory, 'System Direct3DCreate9 did not return a factory'
table = c.cast(factory, c.POINTER(c.POINTER(c.c_void_p))).contents
count = c.WINFUNCTYPE(w.UINT, c.c_void_p)(table[4])(factory)
c.WINFUNCTYPE(w.ULONG, c.c_void_p)(table[2])(factory)
print('PASS: real Windows proxy load, system factory, public method forwarding, Release; adapters=', count)

compiler = c.WinDLL('d3dcompiler_47.dll')
assemble = compiler.D3DAssemble
assemble.argtypes = [c.c_void_p, c.c_size_t, c.c_char_p, c.c_void_p, c.c_void_p, w.UINT, c.POINTER(c.c_void_p), c.POINTER(c.c_void_p)]
assemble.restype = c.c_long
for black in (False, True):
    rgb=0 if black else 0x3f000000
    value='0' if black else '0.5'
    expected = struct.pack('<10I',0x05000051,0xa00f0000,rgb,rgb,rgb,0x3f800000,0x02000001,0x800f0800,0xa0e40000,0x0000ffff)
    for profile in ('ps_2_0', 'ps_3_0'):
        code = (profile+f'\ndef c0, {value}, {value}, {value}, 1\nmov oC0, c0\n').encode()
        blob, errors = c.c_void_p(), c.c_void_p()
        hr = assemble(code,len(code),None,None,None,0,c.byref(blob),c.byref(errors))
        assert hr >= 0, f'D3DAssemble failed for {profile}: {hr}'
        v = c.cast(blob,c.POINTER(c.POINTER(c.c_void_p))).contents
        address = c.WINFUNCTYPE(c.c_void_p,c.c_void_p)(v[3])(blob)
        size = c.WINFUNCTYPE(c.c_size_t,c.c_void_p)(v[4])(blob)
        data = c.string_at(address,size)
        assert expected in data, f'Generated {profile} tokens differ from the Microsoft assembler'
        c.WINFUNCTYPE(w.ULONG,c.c_void_p)(v[2])(blob)
        if errors:
            ev=c.cast(errors,c.POINTER(c.POINTER(c.c_void_p))).contents
            c.WINFUNCTYPE(w.ULONG,c.c_void_p)(ev[2])(errors)
        print('PASS: sky shader tokens match Microsoft D3DAssemble for',profile,'black' if black else 'gray')
