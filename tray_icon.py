"""Windows notification-area icon with a sleeping native message thread. Standard library only."""
import ctypes as c
from ctypes import wintypes as w
from pathlib import Path
import os
import threading

WM_ACTION = 0x8000 + 37
WM_OPEN = 0x8000 + 38
CLASS_NAME = 'TextureLab.NotificationWindow'
WINDOW_TITLE = 'Texture Lab background'

if os.name == 'nt':
    LRESULT = c.c_ssize_t
    WNDPROC = c.WINFUNCTYPE(LRESULT, w.HWND, w.UINT, w.WPARAM, w.LPARAM)
    class WNDCLASS(c.Structure):
        _fields_ = [('style',w.UINT),('proc',WNDPROC),('extra_class',c.c_int),('extra_window',c.c_int),('instance',w.HINSTANCE),('icon',w.HICON),('cursor',w.HANDLE),('background',w.HBRUSH),('menu',w.LPCWSTR),('name',w.LPCWSTR)]
    class GUID(c.Structure):
        _fields_=[('a',w.DWORD),('b',w.WORD),('d',w.WORD),('e',c.c_ubyte*8)]
    class NOTIFYICONDATA(c.Structure):
        _fields_=[('size',w.DWORD),('window',w.HWND),('id',w.UINT),('flags',w.UINT),('message',w.UINT),('icon',w.HICON),('tip',w.WCHAR*128),('state',w.DWORD),('state_mask',w.DWORD),('info',w.WCHAR*256),('version',w.UINT),('title',w.WCHAR*64),('info_flags',w.DWORD),('guid',GUID),('balloon',w.HICON)]

def _apis():
    user=c.WinDLL('user32',use_last_error=True); shell=c.WinDLL('shell32',use_last_error=True); kernel=c.WinDLL('kernel32',use_last_error=True)
    specs = {
        'RegisterClassW':([c.POINTER(WNDCLASS)],w.WORD),
        'UnregisterClassW':([w.LPCWSTR,w.HINSTANCE],w.BOOL),
        'CreateWindowExW':([w.DWORD,w.LPCWSTR,w.LPCWSTR,w.DWORD,c.c_int,c.c_int,c.c_int,c.c_int,w.HWND,w.HMENU,w.HINSTANCE,c.c_void_p],w.HWND),
        'DefWindowProcW':([w.HWND,w.UINT,w.WPARAM,w.LPARAM],LRESULT),
        'DestroyWindow':([w.HWND],w.BOOL),'PostMessageW':([w.HWND,w.UINT,w.WPARAM,w.LPARAM],w.BOOL),
        'GetMessageW':([c.POINTER(w.MSG),w.HWND,w.UINT,w.UINT],c.c_int),
        'TranslateMessage':([c.POINTER(w.MSG)],w.BOOL),'DispatchMessageW':([c.POINTER(w.MSG)],LRESULT),
        'PostQuitMessage':([c.c_int],None),'RegisterWindowMessageW':([w.LPCWSTR],w.UINT),
        'LoadImageW':([w.HINSTANCE,w.LPCWSTR,w.UINT,c.c_int,c.c_int,w.UINT],w.HANDLE),
        'GetSystemMetrics':([c.c_int],c.c_int),'DestroyIcon':([w.HICON],w.BOOL),'CreatePopupMenu':([],w.HMENU),
        'AppendMenuW':([w.HMENU,w.UINT,c.c_size_t,w.LPCWSTR],w.BOOL),
        'TrackPopupMenu':([w.HMENU,w.UINT,c.c_int,c.c_int,c.c_int,w.HWND,c.c_void_p],w.UINT),
        'DestroyMenu':([w.HMENU],w.BOOL),'GetCursorPos':([c.POINTER(w.POINT)],w.BOOL),
        'SetForegroundWindow':([w.HWND],w.BOOL),'FindWindowW':([w.LPCWSTR,w.LPCWSTR],w.HWND)}
    for name,(args,result) in specs.items():
        fn=getattr(user,name);fn.argtypes=args;fn.restype=result
    shell.Shell_NotifyIconW.argtypes=[w.DWORD,c.POINTER(NOTIFYICONDATA)];shell.Shell_NotifyIconW.restype=w.BOOL
    kernel.GetModuleHandleW.argtypes=[w.LPCWSTR];kernel.GetModuleHandleW.restype=w.HMODULE
    return user,shell,kernel

class TrayIcon:
    def __init__(self, icon, callback):
        self.icon_path=str(Path(icon).resolve());self.callback=callback
        self.available=False;self.window=None;self.error=None;self.ready=threading.Event();self.thread=None
    def start(self):
        if os.name!='nt':return False
        self.thread=threading.Thread(target=self._run,name='TextureLab tray',daemon=True);self.thread.start()
        self.ready.wait(3)
        return self.available
    def _run(self):
        user,shell,kernel=_apis();instance=kernel.GetModuleHandleW(None);icon=None;registered=False
        self.user=user
        taskbar=user.RegisterWindowMessageW('TaskbarCreated')
        def add_icon():
            self.available=bool(shell.Shell_NotifyIconW(0,c.byref(self.data)))
        @WNDPROC
        def proc(hwnd,message,wp,lp):
            if message==taskbar:
                add_icon();return 0
            if message==0x111 and wp in (100,101,102):
                self.callback({100:'open',101:'update',102:'exit'}[wp]);return 0
            if message==WM_OPEN:
                self.callback('open');return 0
            if message==WM_ACTION:
                if lp in (0x202,0x203):self.callback('open')
                elif lp in (0x205,0x7b):
                    menu=user.CreatePopupMenu()
                    try:
                        user.AppendMenuW(menu,0,100,'Open sg0hann Boost')
                        user.AppendMenuW(menu,0,101,'Check for updates')
                        user.AppendMenuW(menu,0x800,0,None)
                        user.AppendMenuW(menu,0,102,'Exit')
                        point=w.POINT();user.GetCursorPos(c.byref(point));user.SetForegroundWindow(hwnd)
                        choice=user.TrackPopupMenu(menu,0x100|0x2,point.x,point.y,0,hwnd,None)
                        if choice:self.callback({100:'open',101:'update',102:'exit'}[choice])
                        user.PostMessageW(hwnd,0,0,0)
                    finally:user.DestroyMenu(menu)
                return 0
            if message==0x10:
                user.DestroyWindow(hwnd);return 0
            if message==2:
                user.PostQuitMessage(0);return 0
            return user.DefWindowProcW(hwnd,message,wp,lp)
        self.proc=proc
        try:
            wc=WNDCLASS();wc.proc=proc;wc.instance=instance;wc.name=CLASS_NAME
            if not user.RegisterClassW(c.byref(wc)):raise OSError(c.get_last_error(),'Cannot register tray window')
            registered=True
            self.window=user.CreateWindowExW(0,CLASS_NAME,WINDOW_TITLE,0,0,0,0,0,None,None,instance,None)
            if not self.window:raise OSError(c.get_last_error(),'Cannot create tray window')
            icon=user.LoadImageW(None,self.icon_path,1,user.GetSystemMetrics(49),user.GetSystemMetrics(50),0x10)
            if not icon:raise OSError(c.get_last_error(),'Cannot load tray icon')
            self.data=NOTIFYICONDATA();self.data.size=c.sizeof(self.data);self.data.window=self.window
            self.data.id=1;self.data.flags=1|2|4;self.data.message=WM_ACTION;self.data.icon=icon
            self.data.tip='sg0hann Boost — right-click for Open, updates or Exit'
            add_icon();self.ready.set()
            message=w.MSG()
            while user.GetMessageW(c.byref(message),None,0,0)>0:
                user.TranslateMessage(c.byref(message));user.DispatchMessageW(c.byref(message))
        except Exception as error:self.error=str(error)
        finally:
            self.ready.set();self.available=False
            if hasattr(self,'data'):shell.Shell_NotifyIconW(2,c.byref(self.data))
            if self.window:user.DestroyWindow(self.window)
            if icon:user.DestroyIcon(icon)
            if registered:user.UnregisterClassW(CLASS_NAME,instance)
            self.window=None
    def stop(self):
        if self.window:self.user.PostMessageW(self.window,0x10,0,0)
        if self.thread and self.thread is not threading.current_thread():self.thread.join(2)

def activate_existing():
    if os.name!='nt':return False
    user,_,_=_apis();window=user.FindWindowW(CLASS_NAME,WINDOW_TITLE)
    if window:user.PostMessageW(window,WM_OPEN,0,0)
    return bool(window)
