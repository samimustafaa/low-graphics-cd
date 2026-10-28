# sg0hann BOOST 1.6.10

- Added **Repair installation** for existing d3d9.dll conflicts, missing helpers, damaged records, and changed helpers.
- Repair asks first, keeps the previous files in a BOOST_backup_ folder, and includes undo instructions. Valid BOOST settings are preserved. Failed repairs roll back when possible and retain recovery copies if rollback is blocked.
- Game selection now checks helper integrity before displaying an applied preset. Failed operations no longer leave a green success claim.
- Missing or damaged bundled components now show reinstall and antivirus-history guidance.

Graphics rendering is unchanged: the game helper remains 1.6.7. Opaque structure materials are not included in this release; they require the matching game shader/material files. No FPS gain or antivirus clearance is guaranteed.

Download **sg0hann-BOOST-Setup-1.6.10.exe** or **sg0hann-BOOST-Portable-1.6.10.zip**. Scan results and checksums are included.
