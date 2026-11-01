# sg0hann BOOST 1.6.12

- Protected tree leaf coverage in every preset, including older aggressive saved settings. The helper no longer forces coarse mip levels, texture bias, or mip filters on alpha-capable, mask, compressed, or unknown texture formats. DXT1 is protected because it can contain transparent leaf cutouts.
- Kept texture reduction on explicitly opaque RGB formats. Some other transparent surfaces also keep their original texture detail as part of this conservative fix.
- Added Windows rendering regressions with visible leaf pixels, transparent cutouts, and deliberately transparent lower mips.
- The launcher clearly prompts users to update an older installed graphics helper.

**After updating:** close the game, click **Install / update**, Apply your preset, and relaunch. Updating only the launcher does not replace the helper in the game folder.

The app does not restore game archives changed by other tools. Test foliage in your actual game version after installing this fix.

Download **sg0hann-BOOST-Setup-1.6.12.exe** or **sg0hann-BOOST-Portable-1.6.12.zip**.
