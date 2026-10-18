$ErrorActionPreference = 'Stop'
python -m PyInstaller --noconfirm --clean --onefile --windowed --noupx --name FrozenUpdateProbe --paths . --distpath build/update-probe/dist --workpath build/update-probe/work --specpath build/update-probe --add-binary "$PWD\TextureLab-Updater.exe;." tools/frozen_update_probe.py
if ($LASTEXITCODE) { throw 'Frozen update probe build failed' }
$probe = Join-Path $PWD 'build\update-probe\dist\FrozenUpdateProbe.exe'
$payload = Join-Path $PWD 'build\update-probe\payload'
New-Item -ItemType Directory -Force $payload | Out-Null
Copy-Item $probe (Join-Path $payload 'TextureLab.exe')
$probe = Join-Path $payload 'TextureLab.exe'
$source = Join-Path $PWD 'packaging'
# Compile the actual production installer script with only its source EXE and
# output directory changed. The [Run]/PrepareAppLaunch logic stays identical.
$text = Get-Content packaging/TextureLab.iss -Raw
$text = $text.Replace('[Setup]', "[Setup]`nSourceDir=$source")
$text = $text.Replace('Source: "..\dist\TextureLab.exe"', "Source: `"$probe`"")
$fixture = Join-Path $PWD 'build\update-probe\probe.iss'
$text | Set-Content $fixture
$compiler = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'
$output = Join-Path $PWD 'build\update-probe\installer'
& $compiler "/O$output" '/FFrozenUpdateProbe-Setup' $fixture
if ($LASTEXITCODE) { throw 'Frozen update probe installer build failed' }
python tools/windows_frozen_update_test.py
if ($LASTEXITCODE) { throw 'Frozen-parent update handoff tests failed' }
