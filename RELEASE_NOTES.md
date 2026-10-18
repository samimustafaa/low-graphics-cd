# Texture Lab 1.2.0

- Removed the large “Make room for potato graphics” heading. Added the top navigation, charcoal/lavender layout and a crisp multi-resolution TL icon (16–256 px).
- X keeps the app in the Windows notification area. Right-click for Open, Check for updates or Exit. No automatic Windows startup entry.
- Added update checks on opening, every six hours and manually from About/tray. New releases show an opt-in popup, download with size/SHA-256 checks, then install and reopen. Portable updates use a separate wait/swap/relaunch helper with a previous-copy backup.
- Potato Graphics now requests level-2 as the largest sampled mip on eligible ordinary texture chains, including close-range sampling, and preserves the override after late game sampler writes. It clamps to available levels, restores original state on unbind, and falls back if rejected. The lower-mipmap checkbox also controls this floor. Normal/Low/Ultra behavior is retained.
- Reduced background polling and disabled periodic renderer statistics by default. Enable logging in Diagnostics when needed.

## Install once, then use the updater

Download **TextureLab-Setup-1.2.0.exe** (recommended) or **TextureLab-1.2.0.exe** (portable). Earlier versions need this one manual download to gain automatic updates. Python is bundled; no console is required.

Close the game, open the app, select your client.exe, click **Install / update**, choose Potato Graphics and **Apply preset**, then launch the game normally. An app update keeps your selected game path and game settings; installing the newer game-directory renderer remains a separate explicit action with the game closed.

## Practical limits

This version targets existing lower mipmaps; it does not rewrite game archives, reduce geometry or free full-resolution texture allocations. Non-mipmapped textures and some autogen paths remain unaffected. It cannot identify individual skins/stairs/weapons or promise exactly 70% reduction for them. Real client/GPU testing is still needed; FPS and frame-time improvements are not guaranteed. If the stronger close-up setting causes a visual issue, disable the lower-mipmap checkbox or use Low/Ultra and Apply with the game closed.

Build/test results are in the linked GitHub Actions run: backend/GUI/update failure tests, native sanitizer/SDK checks, real Windows D3D9 sampler-state checks when a device is available, native tray messages, portable updater replacement/relaunch and packaged installer smoke tests. Automated checks do not establish live gameplay performance.
