# Texture Lab 1.5.1

- Replaced small sky radio circles with rounded, animated Gray/Black buttons, clear selection styling and mouse/keyboard support.
- Choosing a color enables the Sky switch. Apply confirms the saved sky color and restart requirement.
- Fixed a sky-recognition gap: `skyauto_new` lacks two constants required by the old matcher. Gray and Black now support its cloud-bearing sky signature, alongside the original sky variants.
- Added real D3D9 pixel tests for Gray, Black and original-sky mode across both shader models and sky signatures.

**Required after updating:** close the game, click **Install / update**, choose **Potato Graphics**, pick **Gray** or **Black**, click **Apply preset**, and relaunch the game. Updating the app alone does not replace the older renderer in the game folder.

Unknown/stripped sky shaders and separate effects may remain unchanged. Existing grass/ground options, texture strengths, icon and updater behavior are preserved.
