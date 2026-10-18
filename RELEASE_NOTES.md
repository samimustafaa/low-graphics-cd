# Texture Lab 1.3.0

- Reference-style stacked charcoal panels, lavender accents and larger preset cards with icons, descriptions and selection markers. The previously removed slogan stays removed.
- Green confirmation after a successful preset save, including the exact saved texture preset. Selecting another card alone does not claim it has been applied.
- Fixed, non-resizable window centered in the work area of the monitor under the pointer on opening. Smaller displays use compact spacing.
- Potato Graphics requests a level-4 mip floor instead of level 2 on eligible chains, clamped to levels actually available. Two extra reductions permit 75% smaller width/height levels than the previous floor where available. This is not an exact “80%” per-skin reduction.
- Added Potato-only handling of mipmapped sky/environment cubemaps using the proper cube-texture interface. Render-target/depth and unsupported non-mipmapped textures remain excluded; original sampler states are restored on unbind. Reflections using ordinary cubemaps may also soften.
- Recognized sky shaders retain flat, texture-free gray shading. Unknown shaders remain untouched. The option cannot guarantee removal of every cloud/effect pass.

## Install / update

Use **About → Check for updates**, or download **TextureLab-Setup-1.3.0.exe** / portable **TextureLab-1.3.0.exe**. Close the game, click **Install / update**, select **Potato Graphics**, then **Apply preset**. This installs the new renderer into the game folder; updating the control app alone does not do that.

The helper requests existing mip levels. Some skins/weapons/characters may use unsupported texture paths and remain detailed. Geometry and full-resolution texture allocations are unchanged. Exact asset-specific percentages, live game compatibility and FPS/frame-time gains need real-client testing; they are not established by the automated checks. Use Low/Ultra, or disable the lower-mipmap option, if the stronger setting causes visual issues.

Windows checks cover real 2D/cubemap sampler state and restoration, UI fit/green confirmation/fixed centered placement, updater/tray behavior, and packaged installation.
