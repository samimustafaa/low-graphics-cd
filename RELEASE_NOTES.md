# sg0hann BOOST 1.6.13

- Restored the previous Low and Ultra texture reduction for opaque materials, including RGBA and compressed textures that 1.6.12 excluded. Normal keeps the game's original texture sampling.
- Kept tree-leaf protection: cutout shaders and alpha-test/blended draws use original sampling. Unknown or unreadable pixel shaders are also protected. Other transparent materials may therefore keep more detail.
- Preset values, sky choices and Ultra options are unchanged. Potato Graphics remains removed.
- Added draw-boundary coverage checks with a bounded shader-analysis cache. No texture readback or archive modifications. Normal/off avoids these extra checks.
- Windows rendering tests cover visible leaves and cutouts, switching the same RGBA/DXT resource between leaf and opaque shaders, and restoring strong opaque reduction.

**To activate the fix:** update the app, close the game, click **Install / update**, then **Apply preset** and relaunch. Updating the launcher alone does not replace the game helper.

Download **sg0hann-BOOST-Setup-1.6.13.exe** or **sg0hann-BOOST-Portable-1.6.13.zip**. Test your actual game client; performance depends on the PC and scene.
