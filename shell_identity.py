"""Windows taskbar relaunch identity, including portable one-file builds.

Keep the AppUserModelID stable across branding and version changes. Icons referenced
by a pinned shortcut must outlive PyInstaller's temporary extraction directory.
"""
import ctypes as c
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid

APP_ID = 'sg0hann.TextureLab'
DISPLAY_NAME = 'sg0hann Boost'

class GUID(c.Structure):
    _fields_ = [('data1',c.c_uint32),('data2',c.c_uint16),('data3',c.c_uint16),('data4',c.c_ubyte*8)]
    @classmethod
    def parse(cls,value): return cls.from_buffer_copy(uuid.UUID(value).bytes_le)

class PropertyKey(c.Structure):
    _fields_ = [('fmtid',GUID),('pid',c.c_uint32)]

class Value(c.Union):
    _fields_ = [('pointer',c.c_void_p),('storage',c.c_byte*(16 if c.sizeof(c.c_void_p)==8 else 8))]

class PropVariant(c.Structure):
    _fields_ = [('vt',c.c_uint16),('reserved1',c.c_uint16),('reserved2',c.c_uint16),('reserved3',c.c_uint16),('value',Value)]

FMTID = '9f4c2855-9f79-4b39-a8d0-e1d42de1d5f3'
IID_STORE = '886d8eeb-8cf2-4446-8d02-cdba1dbdcf99'

def checked(result):
    if result < 0: raise OSError(f'Windows taskbar property error 0x{result & 0xffffffff:08x}')

def method(store,index,result,*args):
    table=c.cast(store,c.POINTER(c.POINTER(c.c_void_p))).contents
    return c.WINFUNCTYPE(result,c.c_void_p,*args)(table[index])

def property_store(window):
    shell=c.WinDLL('shell32')
    shell.SHGetPropertyStoreForWindow.argtypes=[c.c_void_p,c.POINTER(GUID),c.POINTER(c.c_void_p)]
    shell.SHGetPropertyStoreForWindow.restype=c.c_int32
    store=c.c_void_p();iid=GUID.parse(IID_STORE)
    checked(shell.SHGetPropertyStoreForWindow(window,c.byref(iid),c.byref(store)))
    return store

def set_values(window,values):
    store=property_store(window)
    try:
        setter=method(store,6,c.c_int32,c.POINTER(PropertyKey),c.POINTER(PropVariant))
        for pid,text in values:
            key=PropertyKey(GUID.parse(FMTID),pid);value=PropVariant()
            if text is not None:
                buffer=c.create_unicode_buffer(text);value.vt=31
                value.value.pointer=c.cast(buffer,c.c_void_p).value
            checked(setter(store,c.byref(key),c.byref(value)))
        # Window property stores apply SetValue immediately; no Commit needed.
    finally: method(store,2,c.c_uint32)(store)

def read_values(window):
    """Read back the real Shell properties for packaged Windows regression tests."""
    store=property_store(window);values={}
    ole=c.WinDLL('ole32');ole.PropVariantClear.argtypes=[c.POINTER(PropVariant)]
    try:
        getter=method(store,5,c.c_int32,c.POINTER(PropertyKey),c.POINTER(PropVariant))
        for pid in (2,3,4,5):
            key=PropertyKey(GUID.parse(FMTID),pid);value=PropVariant()
            try:
                checked(getter(store,c.byref(key),c.byref(value)))
                values[pid]=c.wstring_at(value.value.pointer) if value.vt==31 and value.value.pointer else None
            finally:ole.PropVariantClear(c.byref(value))
        return values
    finally:method(store,2,c.c_uint32)(store)

def persistent_icon(source,directory=None):
    data=Path(source).read_bytes()
    directory=Path(directory) if directory else Path(os.environ.get('LOCALAPPDATA',Path.home()/'.config'))/'CDTextureLab'/'icons'
    directory.mkdir(parents=True,exist_ok=True)
    target=directory/('sg0hann-boost-'+hashlib.sha256(data).hexdigest()[:16]+'.ico')
    if not target.exists() or target.read_bytes()!=data:
        fd,name=tempfile.mkstemp(prefix='icon-',suffix='.tmp',dir=directory)
        try:
            with os.fdopen(fd,'wb') as output:output.write(data)
            os.replace(name,target)
        finally:
            if os.path.exists(name):os.unlink(name)
    return target.resolve()

def relaunch_command():
    # Never retain --smoke-test arguments or a temporary _MEI path in a pin.
    args=[str(Path(sys.executable).resolve())]
    if not getattr(sys,'frozen',False):args.append(str(Path(__file__).with_name('texture_lab.pyw').resolve()))
    return subprocess.list2cmdline(args)

def configure(window,icon):
    # Set all relaunch data before assigning the explicit window identity.
    path=persistent_icon(icon)
    set_values(window,[(2,relaunch_command()),(3,str(path)+',0'),(4,DISPLAY_NAME),(5,APP_ID)])
    return path

def clear(window):
    set_values(window,[(5,None),(2,None),(3,None),(4,None)])
