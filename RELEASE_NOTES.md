Texture Lab 1.1.0 focuses on the Potato Graphics renderer path and the selected TL icon.

- Potato Graphics now preserves the requested reduction when the game writes sampler bias after binding a texture. Previously those later writes could undo the reduction.
- New optional mipmap correction enables POINT mipmap sampling on eligible textures when the game requests NONE. This can address detailed buildings/trees/distant surfaces whose mipmaps were not being used. It leaves existing LINEAR/POINT filters alone, skips single-level/render-target/depth textures and falls back on API failure.
- Added call-order, restoration, filtering-rejection, state-block and coverage regression tests, plus a real Windows sampler-state probe when a device is available.
- The chosen TL icon is embedded in the app/installer and shown in the sidebar/window.
- Apply shows “You are using {preset} textures” in both the persistent label and status area and scrolls to the label. The game must be closed.
- Diagnostics now count corrected late writes, disabled-mipmap requests, optional filter changes and binds without eligible mipmaps.
- Ultra and Low retain their existing preset values and late-write behavior. Normal/off avoids texture-metadata queries. Gray-sky behavior is unchanged.

Install TextureLab-Setup-1.1.0.exe, close the game, select client.exe, click Install / update, select Potato Graphics and Apply, then relaunch. The optional mipmap checkbox can be disabled separately if it causes visual issues.

These fixes address concrete renderer-state gaps; they do not prove that every building/tree/distant texture is reduced in every client. Non-mipmapped assets cannot be reduced by this method. Exact 50% reduction only for skins/weapons/pickaxes needs asset identification that this helper does not have. FPS and frame-time gains have not been measured in the target game. Binaries are unsigned; SHA256SUMS.txt verifies integrity.
