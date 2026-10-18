"""Windows icon inspection used by release checks; no third-party dependencies."""
import ctypes as c
from ctypes import wintypes as w

def icon_dimensions(window,kind):
    user=c.WinDLL('user32');gdi=c.WinDLL('gdi32')
    user.SendMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM];user.SendMessageW.restype=c.c_ssize_t
    class Info(c.Structure):_fields_=[('icon',w.BOOL),('x',w.DWORD),('y',w.DWORD),('mask',w.HBITMAP),('color',w.HBITMAP)]
    class Bitmap(c.Structure):_fields_=[('type',w.LONG),('width',w.LONG),('height',w.LONG),('stride',w.LONG),('planes',w.WORD),('bits',w.WORD),('memory',c.c_void_p)]
    user.GetIconInfo.argtypes=[w.HICON,c.POINTER(Info)];user.GetIconInfo.restype=w.BOOL
    gdi.GetObjectW.argtypes=[w.HANDLE,c.c_int,c.c_void_p];gdi.GetObjectW.restype=c.c_int
    gdi.DeleteObject.argtypes=[w.HANDLE]
    icon=user.SendMessageW(window,0x7f,kind,0);info=Info()
    assert icon and user.GetIconInfo(icon,c.byref(info)),'Window has no native icon'
    try:
        bitmap=Bitmap();assert info.color and gdi.GetObjectW(info.color,c.sizeof(bitmap),c.byref(bitmap))
        return bitmap.width,bitmap.height
    finally:
        if info.mask:gdi.DeleteObject(info.mask)
        if info.color:gdi.DeleteObject(info.color)
