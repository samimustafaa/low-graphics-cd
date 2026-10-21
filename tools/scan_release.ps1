# Read-only custom scans: no antivirus exclusions or security-setting changes.
$ErrorActionPreference = 'Stop'
$report = [ordered]@{
    utc = [DateTime]::UtcNow.ToString('o')
    status = 'not_run'
    engine = $null
    signatures = $null
    reason = $null
    scans = @()
    virustotal = 'Not submitted or verified by this build'
    authenticode = 'Unsigned; no publisher signing certificate configured'
}
$available = $false
try {
    $state = Get-MpComputerStatus -ErrorAction Stop
    $report.engine = $state.AMEngineVersion
    $report.signatures = $state.AntivirusSignatureVersion
    if ($state.AntivirusEnabled -and $state.AMServiceEnabled) { $available = $true }
    else { $report.reason = 'Microsoft Defender Antivirus service is not enabled on this runner' }
} catch { $report.reason = 'Microsoft Defender status is unavailable on this runner' }
$failed = $false
if ($available) {
    $scanner = Get-ChildItem "$env:ProgramData\Microsoft\Windows Defender\Platform\*\MpCmdRun.exe" -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -First 1 -ExpandProperty FullName
    if (!$scanner) { $scanner = "$env:ProgramFiles\Windows Defender\MpCmdRun.exe" }
    $report.status = 'passed'
    $targets = @((Resolve-Path dist\TextureLab).Path, (Resolve-Path release).Path)
    foreach ($target in $targets) {
        # DisableRemediation is scan-only: it ignores exclusions, scans archives,
        # reports detections in stdout, and does not quarantine the build inputs.
        $output = & $scanner -Scan -ScanType 3 -File $target -DisableRemediation 2>&1
        $code = $LASTEXITCODE
        $report.scans += [ordered]@{ target = (Split-Path $target -Leaf); exit_code = $code; output = ($output | Out-String) }
        if ($code -ne 0) { $failed = $true; $report.status = 'failed_or_scan_error' }
    }
}
$report | ConvertTo-Json -Depth 8 | Set-Content release\SCAN-RESULTS.json
Get-Content release\SCAN-RESULTS.json
if (!$available) { Write-Warning 'Defender scan NOT RUN; this is not an antivirus clearance.' }
if ($failed) { throw 'Defender reported a detection or scan error. Release publication is blocked; inspect scan output.' }
Get-ChildItem release -File | Where-Object Name -ne 'SHA256SUMS.txt' | Sort-Object Name | ForEach-Object { (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower() + '  ' + $_.Name } | Set-Content release\SHA256SUMS.txt
