# Texture Lab 1.3.1

Fixes update/restart handling associated with **Failed to load Python DLL … _MEI…\python312.dll**.

- Update children start with a fresh PyInstaller environment. They no longer reuse the current process's temporary extraction directory after it exits.
- The app sanitizes bundle-owned child search paths and briefly resets Windows DLL search state while launching an external updater; the parent state is restored.
- The portable helper independently prepares a fresh relaunch environment.
- The installer prepares a fresh runtime before reopening Texture Lab, including handoffs from older installed app versions.
- Added real one-file parent/child regression checks for portable, installed, inherited-helper and legacy-installer paths. Previous independent-launch tests did not cover this packaged-parent inheritance path.

If an older updater already showed this error, close it and open Texture Lab again from its shortcut or EXE. The app files may already have updated; the automatic restart was the failed step. You can also run **TextureLab-Setup-1.3.1.exe** for a clean independent upgrade. Older portable updaters may need one manual reopen during their first transition to this fixed version.

The 1.3.0 design, graphics settings and renderer are unchanged. No Python installation or game-helper reinstall is required for this update.
