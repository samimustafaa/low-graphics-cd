$ErrorActionPreference = 'Stop'
$smoke = Join-Path $env:TEMP 'TextureLab-portable-smoke.json'
$p = Start-Process -FilePath "$PWD\dist\TextureLab.exe" -ArgumentList '--smoke-test', "`"$smoke`"" -PassThru
if (!$p.WaitForExit(45000)) { $p.Kill(); throw 'Packaged app did not finish smoke test' }
if ($p.ExitCode -ne 0 -or !(Test-Path $smoke)) { throw 'Packaged app failed smoke test' }
Get-Content $smoke
$target = Join-Path $env:TEMP 'TextureLab-install-test'
$p = Start-Process -FilePath "$PWD\release\TextureLab-Setup-1.0.0.exe" -ArgumentList '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', "/DIR=`"$target`"" -Wait -PassThru
if ($p.ExitCode -ne 0 -or !(Test-Path "$target\TextureLab.exe")) { throw 'Silent installer failed' }
$installed = Join-Path $env:TEMP 'TextureLab-installed-smoke.json'
$p = Start-Process -FilePath "$target\TextureLab.exe" -ArgumentList '--smoke-test', "`"$installed`"" -PassThru
if (!$p.WaitForExit(45000)) { $p.Kill(); throw 'Installed app did not finish smoke test' }
if ($p.ExitCode -ne 0 -or !(Test-Path $installed)) { throw 'Installed app failed smoke test' }
Get-Content $installed
$p = Start-Process -FilePath "$target\unins000.exe" -ArgumentList '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART' -Wait -PassThru
if ($p.ExitCode -ne 0) { throw 'Uninstaller failed' }
