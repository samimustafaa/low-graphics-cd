"""Real Win32 tray messages and portable updater wait/swap/relaunch integration."""
from pathlib import Path
import hashlib
import queue
import shutil
import subprocess
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tray_icon import TrayIcon, activate_existing
tray=TrayIcon('app.ico',lambda action: actions.put(action));actions=queue.Queue()
try:
    tray.start()
    assert tray.window, tray.error
    assert activate_existing()
    assert actions.get(timeout=3)=='open'
    print(f'PASS: native tray creation, activation message, idle message loop; shell icon available={tray.available}')
finally:
    tray.stop()
    assert not tray.thread.is_alive()
with tempfile.TemporaryDirectory(prefix='Texture Lab update ') as temp:
    folder=Path(temp);target=folder/'TextureLab.exe';candidate=folder/'new.exe'
    fixture=Path('native-tests/update_fixture.exe')
    shutil.copy2(fixture,target);shutil.copy2(fixture,candidate)
    # Different file content, still a valid Windows image.
    with candidate.open('ab') as f:f.write(b'Texture Lab update test')
    original=target.read_bytes();digest=hashlib.sha256(candidate.read_bytes()).hexdigest()
    old=subprocess.Popen([str(target),'wait'])
    update=subprocess.Popen([str(Path('TextureLab-Updater.exe').resolve()),str(old.pid),str(candidate),str(target),digest])
    assert update.wait(timeout=30)==0
    old.wait(timeout=5)
    assert target.read_bytes()==candidate.read_bytes()
    assert target.with_name(target.name+'.previous').read_bytes()==original
    import time
    for _ in range(50):
        if Path(str(target)+'.launched').exists():break
        time.sleep(.1)
    assert Path(str(target)+'.launched').exists()
    print('PASS: real updater waits for parent, verifies SHA-256, replaces path with spaces, retains backup and relaunches')
