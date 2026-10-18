# Texture Lab 1.6.0

- Added explicit **Normal (blue)**, **Sky Gray** and **Sky Black** choices. Normal restores the original sky and stays selected when returning to Potato Graphics.
- Sky colors remain separate from ground/floor options.
- Added cached sky-only recognition when a shader is bound, covering recognized shaders created through native/resource device references instead of the helper's creation callback. The cache preserves shader identity, retains a bounded number of references and releases them when the device wrapper closes. Unknown shaders remain unchanged.
- Corrected taskbar icon selection: use the correct native large/small ICO frames instead of offering the 16 px image first.
- Added regression checks for native-created sky shaders, ground color isolation, original-sky mode and actual packaged taskbar icon dimensions.

**Enable:** update the app, close the game, click **Install / update**, select Potato Graphics, choose a sky mode, **Apply preset**, and restart the game. Updating the app alone does not update the game helper.

The supplied screenshot confirms blue output but cannot identify the running client's shader path. This release extends a missed binding path; it cannot guarantee coverage of unknown or stripped shaders. If the sky remains blue, export Diagnostics after closing the game so the helper version, requested mode and match counters can be checked. Ground settings are independent of sky color. Existing pinned shortcuts may retain a cached icon until repinned.
