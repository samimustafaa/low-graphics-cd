"""CI fixture: execute the production updater from a real one-file Python runtime."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import update_manager

if len(sys.argv)==3 and sys.argv[1]=='--parent':
    config_path=Path(sys.argv[2]).resolve();config=json.loads(config_path.read_text())
    os.environ['TEXTURELAB_PROBE_CONFIG']=str(config_path)
    Path(config['parent_report']).write_text(json.dumps({'bundle':sys._MEIPASS,'executable':sys.executable,'pid':os.getpid()}))
    candidate=Path(config['candidate']);digest=hashlib.sha256(candidate.read_bytes()).hexdigest()
    mode=config['mode']
    if mode.startswith('fixed_'):
        update_manager.start_update(candidate,digest,sys._MEIPASS,installed=mode=='fixed_installed')
    elif mode=='legacy_installed':
        # Mimic the installed updater before the fix: preserve the full frozen
        # process environment, then let the new installer repair its handoff.
        subprocess.Popen([str(candidate),'/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/TEXTURELABUPDATE=1','/DIR='+str(Path(sys.executable).parent)],close_fds=True)
    elif mode=='dirty_native_portable':
        helper=Path(config['helper'])
        shutil.copy2(Path(sys._MEIPASS)/'TextureLab-Updater.exe',helper)
        subprocess.Popen([str(helper),str(os.getpid()),str(candidate),sys.executable,digest],close_fds=True)
    else:raise ValueError('Unknown probe mode')
else:
    config=json.loads(Path(os.environ['TEXTURELAB_PROBE_CONFIG']).read_text())
    Path(config['child_report']).write_text(json.dumps({'bundle':sys._MEIPASS,'executable':sys.executable,'runtime_exists':(Path(sys._MEIPASS)/'python312.dll').is_file()}))
