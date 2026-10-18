# Texture Lab

A minimal Windows graphics control app for the 32-bit Direct3D 9 version of Creative Destruction. Built for players who want lower texture detail on modest hardware.

## Install

Download **TextureLab-Setup-1.1.0.exe** from [Releases](https://github.com/samimustafaa/low-graphics-cd/releases). Install and open it. Python is included; no terminal commands are needed. The standalone `TextureLab-1.1.0.exe` is an alternative if you prefer no installation.

1. Close the game completely.
2. Browse to your actual `client.exe`.
3. Click **Install / update** once to install the bundled graphics helper.
4. Choose a preset and click **Apply preset**.
5. Launch the game normally. The app can be closed after applying.

**To change the textures you need to leave the game!** The app checks for the selected game process before saving. The persistent “You are using … textures” label identifies the saved preset for the next launch; it is not live telemetry from a running game.

| Preset | Texture request | Sky |
| --- | --- | --- |
| Normal | Original tracked sampler bias | Original |
| Low | +2 mip bias on eligible textures ≥256 pixels; replaces the former Potato preset | Original |
| Ultra | +10 bias on eligible textures ≥128 pixels; unchanged from 0.6 | Original |
| Potato Graphics | +15 bias on eligible textures ≥32 pixels, including ordinary autogen mipmaps | Optional neutral gray on recognized sky shaders |

Potato Graphics replaces Wide. Version 1.1 preserves its bias even when the game writes sampler state after binding a texture, and can enable POINT mipmap sampling on eligible textures when the game requests NONE. This corrects two renderer paths which could leave nearby or distant surfaces detailed despite the selected preset. The optional filter has its own checkbox; Ultra/Low retain their previous late-write behavior. This does not prove which render path your client uses. Its broader coverage can soften buildings, trees, characters, skins, weapons, tools and interface atlases. The helper cannot reliably separate those asset categories or promise an exact “50% detail” only for characters/weapons. It requests existing lower mipmaps; it does not delete geometry or rewrite original texture files. Single-level textures without generated mipmaps, render targets and depth textures stay unchanged. No new lower-resolution textures are generated. Drivers can clamp requested bias, and textures already using their smallest mipmap cannot get simpler through bias alone.

## Texture coverage and diagnostics

The new mipmap option is **only for Potato Graphics**. It leaves the game's existing LINEAR/POINT filters alone, excludes render-target/depth and non-mipmapped textures, restores tracked original values when an eligible texture is unbound, and falls back if the optional filter request fails. It does not change minification/magnification filters or force a minimum mip level. Normal/off avoids texture-metadata queries.

The log includes `late_bias` (late game bias writes corrected), `disabled_mip` (game requests for no mipmap filtering), `mip_changes` (optional mip-filter changes), and `no_mips` (binds without an eligible mip chain). These help distinguish an unapplied override from textures that have no lower-detail levels. They do not identify asset names or prove FPS improvements.

The chosen TL icon is used in the app, window/taskbar resources and installer. After Apply, the exact saved preset is shown both at the top and in the status area; selecting a different card alone does not change that saved label.

## Neutral sky

Potato Graphics enables the **Neutral gray sky** checkbox by default. It looks for a pixel-shader CTAB comment containing the exact `skycolormid`, `skycolorlow` and `u_bg_color` names found together in the supplied skyauto shader definitions. Recognized sky pixel shaders use a constant gray output with no texture fetches. Original shader model and reflection metadata are preserved. Unknown/stripped shaders are untouched, and failed replacements retain the original shader. The log reports successful replacements as `Neutral gray sky shader created` and periodic `gray_skies` counts.

This is targeted metadata recognition, not proof of the live game's shader identity. A shader with matching metadata elsewhere could also be affected. Separate cloud/effect passes and post-processing may remain visible or tint the gray. If the sky stays blue, export Diagnostics rather than deleting game files. Disable the sky checkbox, Apply with the game closed and relaunch if it causes an issue.

## Performance and recovery

The changes aim to reduce texture sampling detail/bandwidth and simplify recognized sky pixel shading. The app removes configuration-file reads from the render loop, does no full-screen post-processing and needs no running background UI. It does **not** free the original full-size texture allocations, lower geometry counts, fix CPU/network bottlenecks, or guarantee more FPS or better 1% lows. Interception itself adds CPU work. Compare the same route and camera position with Normal and Potato Graphics after the game has warmed up; measure frame times, not just a screenshot of the FPS counter.

Use **Restore original** with the game closed to remove this app's helper. Do this before uninstalling the control app; the Windows uninstaller removes the control app, not helper files in an arbitrary game directory. Ownership/hash checks prevent overwriting or removing another graphics wrapper. Earlier XML/archive modifications are not repaired by this app. Do not install the DLL into a Windows system folder.

Windows 10/11 and a 32-bit x86 Direct3D 9 client are required. Existing ReShade/HiAlgo/DXVK files are not overwritten. Use only where your game/server permits graphics wrappers. No protection bypass, updater, ads, telemetry or automatic uploads are included. New binaries are unsigned; SHA-256 sums verify file integrity, not an antivirus certification. No game assets or third-party HiAlgo binaries are distributed.

## Build and validation

Source is MIT licensed; see `LICENSE.txt`. The tag-triggered [release workflow](.github/workflows/release.yml) builds the x86 DLL, runs Python/Tk tests and native sanitizer tests on Linux, executes SDK-native tests on Windows, attempts a real device/texture sampler-state test (explicitly skipped if no device is available), tests real Direct3D factory forwarding and shader tokens against Microsoft's assembler, then builds the standalone GUI with PyInstaller and the per-user installer with Inno Setup. Portable/installed app smoke tests and silent install/uninstall tests must pass before the release job runs.

Versions 0.5 and 0.6 were reported working by the user. Those reports do not establish the compatibility or performance of this release's new aggressive coverage and gray-sky path. Automated tests do not replace real gameplay on the target GPU/client. Check the workflow result for actual build/test outcomes.

For local source tests:

```sh
python -m unittest discover -s tests -v
```

Native build details are in [native/BUILD.md](native/BUILD.md). On Windows with the built DLL/hash, Python and Inno Setup 6 installed, run `tools/build_windows.ps1` to create the EXEs. Runtime dependency licensing for bundled Python/Tcl/Tk is included by PyInstaller; PyInstaller's bootloader exception permits this distribution.
