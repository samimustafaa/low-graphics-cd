"""Windowless entry point. Open via Open_Texture_Lab.exe or pythonw.exe."""
from pathlib import Path
import sys
try:
    if sys.version_info < (3, 9): raise RuntimeError('Python 3.9 or newer is required.')
    from texture_ui import main
    main()
except Exception:
    import traceback
    error = traceback.format_exc()
    import os
    output = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'CDTextureLab' / 'launcher_error.log'
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(error, encoding='utf-8')
    except OSError: pass
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, 'sg0hann BOOST could not start.\n\n' + error[-1800:] + '\n\nDetails: ' + str(output) + '', 'sg0hann BOOST startup error', 0x10)
    else: raise
