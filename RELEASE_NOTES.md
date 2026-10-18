# Texture Lab 1.4.0

- Added an optional **Black** sky next to **Gray** under Potato Graphics. Gray remains the default.
- Updating the game helper now preserves your applied settings.
- Sky selection is saved when you apply; existing texture preset strengths and updater fixes are unchanged.
- Recognized sky shaders output solid black without texture reads. Unknown shaders remain untouched; clouds and post-processing may still affect the appearance.

**To enable:** close the game, update Texture Lab, click **Install / update**, choose **Potato Graphics**, enable **Sky**, select **Black**, then **Apply preset** and launch the game. Updating only the app does not replace the game helper.

Black is a visual choice; it does not guarantee an extra FPS increase over gray. No separate Python installation is needed.
