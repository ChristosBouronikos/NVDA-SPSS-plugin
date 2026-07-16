# Build SPSS Accessibility Plugin as a distributable NVDA add-on.
# Author: Bouronikos Christos
# Email: chrisbouronikos@gmail.com
# Donation: https://paypal.me/christosbouronikos

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$manifest = Get-Content "manifest.ini"
$addonName = (($manifest | Select-String '^\s*name\s*=' | Select-Object -First 1) -replace '^[^=]+=', '').Trim().Trim('"')
$version = (($manifest | Select-String '^\s*version\s*=' | Select-Object -First 1) -replace '^[^=]+=', '').Trim().Trim('"')

if ([string]::IsNullOrWhiteSpace($addonName) -or [string]::IsNullOrWhiteSpace($version)) {
	throw "name/version missing from manifest.ini"
}

$distDir = Join-Path $scriptDir "dist"
$outputFile = "$addonName-$version.nvda-addon"
$outputPath = Join-Path $distDir $outputFile
$tempZip = "$outputPath.zip"
$stageDir = Join-Path ([System.IO.Path]::GetTempPath()) "spssAccessibility-addon-stage"

Write-Host "Building SPSS Accessibility Plugin NVDA Add-on"
Write-Host "=============================================="
Write-Host "Version: $version"
Write-Host "Output: $outputPath"
Write-Host ""

if (Test-Path $stageDir) {
	Remove-Item $stageDir -Recurse -Force
}
if (Test-Path $outputPath) {
	Remove-Item $outputPath -Force
}
if (Test-Path $tempZip) {
	Remove-Item $tempZip -Force
}

New-Item -ItemType Directory -Force -Path $distDir | Out-Null
New-Item -ItemType Directory -Force -Path $stageDir | Out-Null

$addonRoot = (Resolve-Path "addon").Path
Get-ChildItem "addon" -Recurse -File | Where-Object {
	$_.Name -notlike "*.pyc" -and
	$_.Name -ne ".DS_Store" -and
	$_.Name -notlike "*.po" -and
	$_.FullName -notmatch "__pycache__" -and
	$_.FullName -notmatch "\\.git" -and
	$_.FullName -notmatch "\\doc\\"
} | ForEach-Object {
	$relative = $_.FullName.Substring($addonRoot.Length).TrimStart(
		[System.IO.Path]::DirectorySeparatorChar,
		[System.IO.Path]::AltDirectorySeparatorChar
	)
	$destination = Join-Path $stageDir $relative
	$destinationDir = Split-Path -Parent $destination
	New-Item -ItemType Directory -Force -Path $destinationDir | Out-Null
	Copy-Item $_.FullName $destination -Force
}

Copy-Item "manifest.ini" (Join-Path $stageDir "manifest.ini") -Force
Copy-Item "LICENSE" (Join-Path $stageDir "LICENSE") -Force

New-Item -ItemType Directory -Force -Path (Join-Path $stageDir "doc\en") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $stageDir "doc\el") | Out-Null
Copy-Item "README.md" (Join-Path $stageDir "doc\en\readme.md") -Force
Copy-Item "docs\README.el.md" (Join-Path $stageDir "doc\el\readme.md") -Force
Copy-Item "CHANGELOG.md" (Join-Path $stageDir "doc\en\changelog.md") -Force
Copy-Item "docs\CHANGELOG.el.md" (Join-Path $stageDir "doc\el\changelog.md") -Force

Compress-Archive -Path (Join-Path $stageDir "*") -DestinationPath $tempZip -Force
Move-Item $tempZip $outputPath -Force

$sha = (Get-FileHash -Path $outputPath -Algorithm SHA256).Hash.ToLowerInvariant()
Set-Content -Path (Join-Path $distDir "SHA256SUMS") -Value "$sha  $outputFile" -Encoding ASCII

Remove-Item $stageDir -Recurse -Force

Write-Host ""
Write-Host "Build complete: $outputPath"
Write-Host ""
Write-Host "Package ready for NVDA Add-on Store submission."
