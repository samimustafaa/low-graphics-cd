$ErrorActionPreference = 'Stop'
python -m pip install -r requirements-build.txt
if ($LASTEXITCODE) { throw 'Build dependencies failed' }
# Main distribution: a visible runtime folder, no extraction at each app launch.
python -m PyInstaller --noconfirm --clean --onedir --windowed --noupx --name TextureLab --icon app.ico --version-file packaging/version_info.txt --add-data 'd3d9.dll:.' --add-data 'DLL_SHA256.txt:.' --add-data 'app.ico:.' --add-data 'app-mark.png:.' --add-data 'icons:icons' texture_lab.pyw
if ($LASTEXITCODE) { throw 'App folder build failed' }
$compiler = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'
if (!(Test-Path $compiler)) { throw 'Install Inno Setup 6 before building the installer' }
& $compiler packaging\TextureLab.iss
if ($LASTEXITCODE) { throw 'Installer build failed' }
# Compatibility alias for app versions that still request the old asset name.
Copy-Item release\sg0hann-BOOST-Setup-1.6.9.exe release\TextureLab-Setup-1.6.9.exe
Compress-Archive -Path dist\TextureLab -DestinationPath release\sg0hann-BOOST-Portable-1.6.9.zip -Force
# One transitional asset preserves the filenames older portable updaters require.
# Its next update migrates to the normal installer; new users use Setup or ZIP.
python -m PyInstaller --noconfirm --clean --onefile --windowed --noupx --name TextureLab --distpath dist/legacy --workpath build/legacy --specpath build/legacy --icon "$PWD\app.ico" --version-file "$PWD\packaging\version_info.txt" --add-data "$PWD\d3d9.dll;." --add-data "$PWD\DLL_SHA256.txt;." --add-data "$PWD\app.ico;." --add-data "$PWD\app-mark.png;." --add-data "$PWD\icons;icons" --add-binary "$PWD\TextureLab-Updater.exe;." "$PWD\texture_lab.pyw"
if ($LASTEXITCODE) { throw 'Legacy update bridge build failed' }
Copy-Item dist\legacy\TextureLab.exe release\TextureLab-1.6.9.exe
$bundle = (Resolve-Path dist\TextureLab).Path
Get-ChildItem $bundle -Recurse -File | Sort-Object FullName | ForEach-Object { (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower() + '  ' + $_.FullName.Substring($bundle.Length + 1).Replace('\','/') } | Set-Content release\PAYLOAD-SHA256SUMS.txt
Get-ChildItem release -File | Where-Object Name -ne 'SHA256SUMS.txt' | Sort-Object Name | ForEach-Object { (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower() + '  ' + $_.Name } | Set-Content release\SHA256SUMS.txt
