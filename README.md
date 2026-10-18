# Texture Lab

A minimal Windows graphics control app for the 32-bit Direct3D 9 version of Creative Destruction. Built for players who want lower texture detail on modest hardware.

## Install

Download **TextureLab-Setup-1.5.0.exe** from [Releases](https://github.com/samimustafaa/low-graphics-cd/releases). Install and open it. Python is included; no terminal commands are needed. The standalone `TextureLab-1.5.0.exe` is an alternative if you prefer no installation.

1. Close the game completely.
2. Browse to your actual `client.exe`.
3. Click **Install / update** once to install the bundled graphics helper.
4. Choose a preset and click **Apply preset**.
5. Launch the game normally. The app can stay in the tray after applying; right-click its icon and choose Exit to quit.

**To change the textures you need to leave the game!** The app checks for the selected game process before saving. The persistent “You are using … textures” label identifies the saved preset for the next launch; it is not live telemetry from a running game.

| Preset | Texture request | Sky |
| --- | --- | --- |
| Normal | Original tracked sampler bias | Original |
| Low | +2 mip bias on eligible textures ≥256 pixels; replaces the former Potato preset | Original |
| Ultra | +10 bias on eligible textures ≥128 pixels; unchanged from 0.6 | Original |
| Potato Graphics | +15 bias on eligible textures ≥32 pixels, including ordinary autogen mipmaps and compatible mipmapped sky/environment cubemaps | Optional neutral gray on recognized sky shaders |

Potato Graphics replaces Wide. Version 1.3 limits the largest sampled mipmap to level 4 for compatible ordinary mip chains, clamped to the available chain. This requests one-sixteenth width/height levels even up close, clamped to the available chain. Compared with the previous level-2 floor, it permits levels with 75% smaller dimensions. This is a sampling request, not an exact per-character quality percentage. It preserves its bias even when the game writes sampler state after binding a texture, and can enable POINT mipmap sampling on eligible textures when the game requests NONE. This corrects two renderer paths which could leave nearby or distant surfaces detailed despite the selected preset. The optional filter has its own checkbox; Ultra/Low retain their previous late-write behavior. This does not prove which render path your client uses. Its broader coverage can soften buildings, trees, characters, skins, weapons, tools and interface atlases. The helper cannot reliably separate those asset categories or promise an exact “80% additional reduction” only for lobby skins, characters or weapons. It requests existing lower mipmaps; it does not delete geometry or rewrite original texture files. Single-level textures without generated mipmaps, render targets and depth textures stay unchanged. No new lower-resolution textures are generated. Drivers can clamp requested bias, and textures already using their smallest mipmap cannot get simpler through bias alone.

## Texture coverage and diagnostics

The new mipmap option is **only for Potato Graphics**. It leaves the game's existing LINEAR/POINT filters alone, excludes render-target/depth and non-mipmapped textures, restores tracked original values when an eligible texture is unbound, and falls back if the optional filter request fails. It does not change minification/magnification filters and requests a level-4 mip floor only when the option is on and a compatible chain reports multiple levels. It does not force a floor on autogen textures reporting only one accessible level. Normal/off avoids texture-metadata queries.

Periodic renderer statistics are **off by default** to reduce disk writes. Enable them in Diagnostics, save with the game closed and restart the game when investigating coverage. With statistics enabled, the log includes `mip_floor` (close-range level changes), `late_bias` (late game bias writes corrected), `disabled_mip` (game requests for no mipmap filtering), `mip_changes` (optional mip-filter changes), and `no_mips` (binds without an eligible mip chain). These help distinguish an unapplied override from textures that have no lower-detail levels. They do not identify asset names or prove FPS improvements.

The chosen TL icon is used in the app, window/taskbar resources and installer. After Apply, the exact saved preset is shown both at the top and in the status area; selecting a different card alone does not change that saved label.

## Neutral sky

Potato Graphics enables the **Sky · Potato Graphics** switch by default. It looks for a pixel-shader CTAB comment containing the exact `skycolormid`, `skycolorlow` and `u_bg_color` names found together in the supplied skyauto shader definitions. Recognized sky pixel shaders use a constant gray or black output (choose **Gray** or **Black**) with no texture fetches. Original shader model and reflection metadata are preserved. Unknown/stripped shaders are untouched, and failed replacements retain the original shader. The log reports successful replacements as `Neutral gray sky shader created` and periodic `gray_skies` counts.

This is targeted metadata recognition, not proof of the live game's shader identity. A shader with matching metadata elsewhere could also be affected. Separate cloud/effect passes and post-processing may remain visible or tint the gray. If the sky stays blue, export Diagnostics rather than deleting game files. Disable the sky checkbox, Apply with the game closed and relaunch if it causes an issue.

## Performance and recovery

The changes aim to reduce texture sampling detail/bandwidth and simplify recognized sky pixel shading. The app removes configuration-file reads from the render loop, does no full-screen post-processing and needs no running background UI. It does **not** free the original full-size texture allocations, lower geometry counts, fix CPU/network bottlenecks, or guarantee more FPS or better 1% lows. Interception itself adds CPU work. Compare the same route and camera position with Normal and Potato Graphics after the game has warmed up; measure frame times, not just a screenshot of the FPS counter.

Use **Restore original** with the game closed to remove this app's helper. Do this before uninstalling the control app; the Windows uninstaller removes the control app, not helper files in an arbitrary game directory. Ownership/hash checks prevent overwriting or removing another graphics wrapper. Earlier XML/archive modifications are not repaired by this app. Do not install the DLL into a Windows system folder.

Windows 10/11 and a 32-bit x86 Direct3D 9 client are required. Existing ReShade/HiAlgo/DXVK files are not overwritten. Use only where your game/server permits graphics wrappers. No protection bypass, ads, telemetry or automatic uploads are included. Update checks contact GitHub as described below. New binaries are unsigned; SHA-256 sums verify file integrity, not an antivirus certification. No game assets or third-party HiAlgo binaries are distributed.

## Build and validation

Source is MIT licensed; see `LICENSE.txt`. The tag-triggered [release workflow](.github/workflows/release.yml) builds the x86 DLL, runs Python/Tk tests and native sanitizer tests on Linux, executes SDK-native tests on Windows, attempts a real device/texture sampler-state test (explicitly skipped if no device is available), tests real Direct3D factory forwarding and shader tokens against Microsoft's assembler, then builds the standalone GUI with PyInstaller and the per-user installer with Inno Setup. Portable/installed app smoke tests and silent install/uninstall tests must pass before the release job runs.

Earlier versions were reported working by the user. Those reports do not establish the compatibility or performance of this release's new aggressive coverage and gray-sky path. Automated tests do not replace real gameplay on the target GPU/client. Check the workflow result for actual build/test outcomes.

For local source tests:

```sh
python -m unittest discover -s tests -v
```

Native build details are in [native/BUILD.md](native/BUILD.md). On Windows with the built DLL/hash and TextureLab-Updater.exe, Python and Inno Setup 6 installed, run `tools/build_windows.ps1` to create the EXEs. Runtime dependency licensing for bundled Python/Tcl/Tk is included by PyInstaller; PyInstaller's bootloader exception permits this distribution.

## Background mode and automatic updates

Install 1.2.0 once to receive the updater; older releases cannot update themselves. The standalone app checks this repository's latest stable GitHub release on opening and every five minutes while running. A popup offers a newer version; nothing downloads or installs until accepted. About and the tray menu also offer **Check for updates**. Failed automatic checks stay quiet. A failed manual check/download shows an error and leaves the app installed.

Downloads use HTTPS, repository/version/filename checks, a 64 MiB bound, exact size and SHA-256 verification from the release's checksum file. This is integrity verification against the GitHub release, not independent publisher authentication. Installed copies use the per-user installer and reopen after an update. Portable copies use a separate bundled helper that waits for the app to exit, verifies the staged executable, retains `.previous`, swaps and relaunches; failed swaps/launches attempt restoration. Protected/read-only portable folders may require moving the app to a writable folder or using the installer. Updating the control app does not replace an already installed game-directory graphics helper: close the game and click **Install / update** to install the new bundled renderer, then Apply.

X hides the window when Windows accepts its tray icon. Right-click it for Open, Check for updates or Exit. If no tray icon can be created, X exits so the app cannot become inaccessible. No Windows startup entry is added. A second launch activates the existing instance. The tray thread waits for native messages, hidden UI polling slows to once per second, and hover animations run only during interaction. No extra tray/update Python dependencies are required.

## 1.3.0 layout and stronger Potato Graphics

The reference design is reflected in stacked rounded charcoal panels, lavender preset cards with icons/descriptions/radio markers, an Apply button, and a green saved-preset confirmation. Selection alone does not change the applied label; failed writes do not report a new preset. The app opens centered in the work area of the monitor under the pointer and has a fixed size. It chooses a smaller compact layout when the available display height requires it. Windows title bars remain dark where supported.

Potato Graphics now covers ordinary mipmapped cubemaps (commonly used for skies/environment maps) through their own Direct3D interface. This can also soften reflections. Render-target/depth cubemaps and unsupported non-mipmapped resources are excluded. Other presets retain their previous scope. The optional recognized-sky replacement already outputs a flat gray color without texture reads; unknown sky shaders are not replaced. The app cannot identify character/weapon/skin assets individually or guarantee they all use eligible mip chains.

After updating the app, close the game, click **Install / update**, select **Potato Graphics**, and **Apply preset** to install the 1.3.0 renderer and use the stronger settings. A control-app update alone does not replace the DLL in the game directory.

## 1.3.1 updater restart fix

Detached update processes now receive a fresh PyInstaller environment instead of inheriting the running app's extraction folder. The app removes private bootloader variables and bundle-owned search paths from the child environment, requests a fresh one-file launch, and temporarily resets Windows DLL search state around spawning the updater. The original app process's environment/search state is retained.

The portable helper independently resets its relaunch environment. The installer also requests a fresh runtime before reopening the app, including when launched by an older installed updater. This fixes the restart path associated with `Failed to load Python DLL ... _MEI.../python312.dll` after the parent app removes its temporary folder. If an older portable updater hits this error during its first transition, close the error and open the updated EXE directly from Explorer; that independent launch does not inherit the old process environment.

New regression fixtures build actual one-file parent and child executables, exercise portable and installed updates, and assert different runtime folders plus removal of the original folder. They also test the new native helper with a deliberately inherited environment and the new installer launched the way older app versions launched it. The game renderer remains 1.3.0; no game-helper reinstall is needed for this updater-only fix.

## 1.4.0 optional black sky

Close the game, update the app, click **Install / update** for the new renderer, choose **Potato Graphics**, enable **Sky**, select **Black**, and click **Apply preset**. Launch the game again. **Gray** remains the default; turn Sky off for the original sky. Texture strengths and updater fixes are unchanged. Only recognized sky shaders change; clouds or post-processing may still affect the final sky. Black is a visual option, not an additional guaranteed FPS increase over gray.

## 1.5.0 no grass, flat ground and visible updates

Close the game, update the app, click **Install / update**, choose **Potato Graphics**, enable **No grass + flat ground**, and **Apply preset**. Restart the game. The option is off by default; Low/Ultra and sky choices retain their existing behavior. Recognized grass vertex shaders collapse to a single clipped position, removing rendered grass and its depth. Recognized terrain pixel shaders output muted green without terrain texture reads. Terrain geometry, hills and collision stay intact. Exact constant-name combinations from the supplied shader sources identify eligible shaders. Unknown/stripped, water and hole shaders remain original; rejected replacements retain the original shader. The running client needs an in-game coverage/performance check. Look for **No grass shader created** and **Flat ground shader created** in its diagnostic log. Disable, Apply and restart to restore those shaders.

A bold, clickable **New update - update the app now** banner stays visible on every page after a newer compatible release is detected, even if its popup is dismissed. Checks run on opening and every five minutes while open or in the tray. Publish a newer numbered GitHub release with the Windows executable assets and checksums to trigger it; source commits alone do not trigger update notices.

The TL icon has a vector master, 1024 px brand image, native PNG frames and a multi-size Windows ICO. Tk and the tray use native frames instead of rough subsampling. Regenerate assets with `python tools/build_icons.py` (Pillow needed only to build). Existing pinned shortcuts may need repinning if Windows cached their previous icon.
