$ErrorActionPreference = 'Stop'
$smoke = Join-Path $env:TEMP 'TextureLab-portable-smoke.json'
$p = Start-Process -FilePath "$PWD\dist\TextureLab.exe" -ArgumentList '--smoke-test', "`"$smoke`"" -PassThru
if (!$p.WaitForExit(45000)) { $p.Kill(); throw 'Packaged app did not finish smoke test' }
if ($p.ExitCode -ne 0 -or !(Test-Path $smoke)) { throw 'Packaged app failed smoke test' }
Get-Content $smoke
$result = Get-Content $smoke -Raw | ConvertFrom-Json
if (!$result.bundle_hash_ok -or !$result.fake_install_apply_restore_ok) { throw "Packaged smoke assertions failed: $(Get-Content $smoke -Raw)" }
$target = Join-Path $env:TEMP 'TextureLab-install-test'
$p = Start-Process -FilePath "$PWD\release\TextureLab-Setup-1.6.7.exe" -ArgumentList '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', "/DIR=`"$target`"" -Wait -PassThru
if ($p.ExitCode -ne 0 -or !(Test-Path "$target\TextureLab.exe")) { throw 'Silent installer failed' }
if (!(Test-Path "$target\TextureLab-installed.txt")) { throw 'Installed update marker missing' }
# Check the shortcut Windows can select when the app is pinned.
$link = Join-Path ([Environment]::GetFolderPath('Programs')) 'sg0hann Boost\sg0hann Boost.lnk'
if (!(Test-Path $link)) { throw 'Branded Start menu shortcut missing' }
$shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut($link)
python -c "import os,sys; assert os.path.samefile(sys.argv[1],sys.argv[2]), sys.argv[1:]" $shortcut.TargetPath "$target\TextureLab.exe"
if ($LASTEXITCODE) { throw "Shortcut launch target is wrong: $($shortcut.TargetPath) vs $target\TextureLab.exe" }
if ($shortcut.IconLocation -notlike '*sg0hann-boost.ico*') { throw 'Shortcut icon is wrong' }
$shell = New-Object -ComObject Shell.Application
$item = $shell.NameSpace((Split-Path $link)).ParseName((Split-Path $link -Leaf))
if ($item.ExtendedProperty('System.AppUserModel.ID') -ne 'sg0hann.TextureLab') { throw 'Shortcut AppUserModelID is wrong' }
$metadata = (Get-Item "$target\TextureLab.exe").VersionInfo
if ($metadata.ProductName -ne 'sg0hann Boost' -or $metadata.FileDescription -ne 'sg0hann Boost') { throw 'Branded EXE metadata missing' }
Write-Host 'PASS: branded shortcut, persistent shortcut icon, matching AppUserModelID and EXE metadata'
$installed = Join-Path $env:TEMP 'TextureLab-installed-smoke.json'
$p = Start-Process -FilePath "$target\TextureLab.exe" -ArgumentList '--smoke-test', "`"$installed`"" -PassThru
if (!$p.WaitForExit(45000)) { $p.Kill(); throw 'Installed app did not finish smoke test' }
if ($p.ExitCode -ne 0 -or !(Test-Path $installed)) { throw 'Installed app failed smoke test' }
Get-Content $installed
$result = Get-Content $installed -Raw | ConvertFrom-Json
if (!$result.bundle_hash_ok -or !$result.fake_install_apply_restore_ok) { throw "Installed smoke assertions failed: $(Get-Content $installed -Raw)" }
python tools/windows_app_lifecycle_test.py "$target"
if ($LASTEXITCODE) { throw 'Installed update/relaunch and background lifecycle test failed' }
$p = Start-Process -FilePath "$target\unins000.exe" -ArgumentList '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART' -Wait -PassThru
if ($p.ExitCode -ne 0) { throw 'Uninstaller failed' }

& ./tools/build_frozen_update_probe.ps1
if ($LASTEXITCODE) { throw 'Frozen update regression tests failed' }
