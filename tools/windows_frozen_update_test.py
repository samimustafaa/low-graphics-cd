"""Regression: restart after a real frozen parent's _MEI directory is removed."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import tempfile
import time

probe=Path('build/update-probe/dist/FrozenUpdateProbe.exe').resolve()
installer=Path('build/update-probe/installer/FrozenUpdateProbe-Setup.exe').resolve()
assert probe.is_file() and installer.is_file()
def until(predicate,timeout=45):
    end=time.monotonic()+timeout
    while time.monotonic()<end:
        if predicate():return
        time.sleep(.1)
    raise AssertionError('Frozen update handoff did not complete')

for mode in ('fixed_portable','dirty_native_portable','fixed_installed','legacy_installed'):
    with tempfile.TemporaryDirectory(prefix='Texture Lab frozen handoff ') as temp:
        folder=Path(temp);target=folder/'app'/'TextureLab.exe';target.parent.mkdir()
        shutil.copy2(probe,target)
        portable='portable' in mode
        candidate=folder/('next.exe' if portable else 'next-setup.exe')
        shutil.copy2(probe if portable else installer,candidate)
        if portable:
            with candidate.open('ab') as f:f.write(b'new update probe overlay')
        config={'mode':mode,'candidate':str(candidate),'parent_report':str(folder/'parent.json'),
                'child_report':str(folder/'child.json'),'helper':str(folder/'TextureLab-Updater.exe')}
        path=folder/'config.json';path.write_text(json.dumps(config))
        env=dict(os.environ)
        for key in list(env):
            if key.startswith('_PYI_') or key=='_MEIPASS2':del env[key]
        env['PYINSTALLER_RESET_ENVIRONMENT']='1'
        parent=subprocess.Popen([str(target),'--parent',str(path)],env=env)
        assert parent.wait(timeout=30)==0,mode
        until(lambda:Path(config['parent_report']).is_file())
        first=json.loads(Path(config['parent_report']).read_text())
        until(lambda:Path(config['child_report']).is_file())
        second=json.loads(Path(config['child_report']).read_text())
        assert second['runtime_exists'],mode
        assert first['bundle']!=second['bundle'],mode
        until(lambda:not Path(first['bundle']).exists())
        until(lambda:not Path(second['bundle']).exists())
        assert Path(second['executable']).resolve()==target.resolve()
        if portable:assert Path(str(target)+'.previous').is_file()
        else:
            uninstall=target.parent/'unins000.exe'
            assert uninstall.is_file()
            subprocess.run([str(uninstall),'/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART'],check=True,timeout=30)
        print(f'PASS: {mode}: fresh Python DLL/runtime, original _MEI removed, updated executable relaunched')
