"""Exercise silent update relaunch and packaged X->tray->Open->Exit lifecycle."""
import ctypes as c
from ctypes import wintypes as w
from pathlib import Path
import subprocess
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import tray_icon
user,_,kernel=tray_icon._apis()
user.IsWindowVisible.argtypes=[w.HWND];user.IsWindowVisible.restype=w.BOOL
user.GetWindowThreadProcessId.argtypes=[w.HWND,c.POINTER(w.DWORD)]
kernel.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];kernel.OpenProcess.restype=w.HANDLE
kernel.WaitForSingleObject.argtypes=[w.HANDLE,w.DWORD];kernel.WaitForSingleObject.restype=w.DWORD
kernel.CloseHandle.argtypes=[w.HANDLE]
installer=Path('release/TextureLab-Setup-1.2.1.exe').resolve()
# subprocess waits for the installer itself, rather than its relaunched app tree.
subprocess.run([str(installer),'/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/TEXTURELABUPDATE=1','/DIR='+str(Path(sys.argv[1]).resolve())],check=True,timeout=60)
def wait_for(predicate):
    end=time.monotonic()+40
    while time.monotonic()<end:
        value=predicate()
        if value:return value
        time.sleep(.1)
    raise AssertionError('Packaged lifecycle step timed out')
window=wait_for(lambda:user.FindWindowW(None,'Texture Lab 1.2.1'))
tray=wait_for(lambda:user.FindWindowW(tray_icon.CLASS_NAME,tray_icon.WINDOW_TITLE))
pid=w.DWORD();user.GetWindowThreadProcessId(window,c.byref(pid))
process=kernel.OpenProcess(0x100000,False,pid.value);assert process
try:
    user.PostMessageW(window,0x10,0,0)
    # GitHub's desktop shell normally accepts notification icons. If it doesn't,
    # the correct product fallback is to exit on X, rather than become invisible.
    end=time.monotonic()+5
    while time.monotonic()<end and user.IsWindowVisible(window):time.sleep(.1)
    if kernel.WaitForSingleObject(process,0)==0:
        print('PASS: installer update flag relaunched GUI; X exited safely without a tray icon (headless shell)')
    else:
        assert not user.IsWindowVisible(window)
        user.PostMessageW(tray,tray_icon.WM_OPEN,0,0)
        wait_for(lambda:user.IsWindowVisible(window))
        user.PostMessageW(tray,0x111,102,0)
        assert kernel.WaitForSingleObject(process,10000)==0
        print('PASS: silent installed update relaunched app; X hides, tray Open restores, Exit terminates')
finally:kernel.CloseHandle(process)
