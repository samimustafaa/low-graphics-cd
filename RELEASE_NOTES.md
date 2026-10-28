# sg0hann BOOST 1.6.10

- Added **Repair installation** for existing d3d9.dll conflicts, missing helpers, damaged records, and changed helpers.
- Repair asks first, keeps the previous files in a BOOST_backup_ folder, and includes undo instructions. Valid BOOST settings are preserved. Failed repairs roll back when possible and retain recovery copies if rollback is blocked.
- Game selection now checks helper integrity before displaying an applied preset. Failed operations no longer leave a green success claim.
- Missing or damaged bundled components now show reinstall and antivirus-history guidance.

- Added optional **Opaque structures (experimental)** under **Potato Graphics**. Recognized scene_cj/scene_cj_pbr shader signatures force final structure opacity while preserving RGB, geometry, cutouts, and unrelated materials. Unrecognized variants remain unchanged.
- The helper is now 1.6.10. After updating the app, close the game and click **Install / update** (or **Repair installation** if needed), enable the option, Apply, and relaunch.

Synthetic renderer checks do not replace testing in your game version. No FPS gain, elimination of drops, or antivirus clearance is guaranteed.

Download **sg0hann-BOOST-Setup-1.6.10.exe** or **sg0hann-BOOST-Portable-1.6.10.zip**. Scan results and checksums are included.
