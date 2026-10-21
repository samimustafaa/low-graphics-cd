# sg0hann Boost 1.6.8

- **Recommended: TextureLab-Setup-1.6.8.exe.** The installed app now uses a normal runtime folder instead of unpacking Python into a temporary directory on every launch.
- Added **sg0hann-Boost-Portable-1.6.8.zip**. Extract the whole folder and run TextureLab.exe inside it.
- Preserved installed updates. ZIP users are told when an update will install the app.
- **TextureLab-1.6.8.exe is a transitional one-file compatibility build** for older portable updaters; its future updates use the regular installer. New users should choose Setup or ZIP.
- Added payload checksums and SCAN-RESULTS.json. This reports whether Defender could run, its engine/signature versions, and scan output. A reported detection or scan error blocks publication. An unavailable scan is explicitly marked not run.

These packaging changes do not establish a clean VirusTotal result. Builds remain unsigned because no publisher signing certificate is configured. The graphics helper is still 1.6.7; game settings and recovery backups are unchanged.
