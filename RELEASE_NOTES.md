Texture Lab 1.0.0 packages the control app as a standalone Windows executable and a per-user installer. Python is included.

- Four presets: Normal, Low (former Potato), Ultra (unchanged), and Potato Graphics (formerly Wide).
- Potato Graphics requests +15 mip bias, covers textures down to 32 pixels and allows ordinary autogen mipmaps. Render targets/depth textures remain excluded.
- Optional neutral gray output for sky shaders recognized from their sky-specific metadata. Unrecognized shaders remain unchanged; replacement failures retain the original shader.
- Minimal dark/gray interface, animated hover/press buttons, persistent saved-preset label, and red game-exit notice.
- The game must be closed before Apply. Settings are read at startup, removing periodic INI reads from the rendering path.
- Restore-original, hash checks, upgrade rollback and diagnostic export remain available.

Install `TextureLab-Setup-1.0.0.exe`, open the app, choose client.exe, Install / update, select a preset and Apply while the game is closed. Then launch the game normally. `TextureLab-1.0.0.exe` is the portable alternative.

Sky recognition needs retained shader metadata and may not match every client. Texture reduction can also blur HUD/characters and does not selectively provide an exact 50% detail setting. Original texture allocations and geometry remain. FPS/stutter improvements are hardware dependent and have not been measured in Creative Destruction for this release. Use Restore original before uninstalling the control app. Binaries are unsigned; SHA256SUMS.txt is provided for integrity verification.
