$ErrorActionPreference = 'Stop'
python -m pip install -r requirements-build.txt
if ($LASTEXITCODE) { throw 'Build dependencies failed' }
python -m PyInstaller --noconfirm --clean --onefile --windowed --noupx --name TextureLab --icon app.ico --add-data 'd3d9.dll:.' --add-data 'DLL_SHA256.txt:.' --add-data 'app.ico:.' texture_lab.pyw
if ($LASTEXITCODE) { throw 'Standalone build failed' }
$compiler = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'
if (!(Test-Path $compiler)) { throw 'Install Inno Setup 6 before building the installer' }
& $compiler packaging\TextureLab.iss
if ($LASTEXITCODE) { throw 'Installer build failed' }
Copy-Item dist\TextureLab.exe release\TextureLab-1.0.0.exe
Get-ChildItem release\*.exe | ForEach-Object { (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower() + '  ' + $_.Name } | Set-Content release\SHA256SUMS.txt
