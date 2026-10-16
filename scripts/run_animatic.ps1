[CmdletBinding()]
param([switch]$Build,[switch]$Stills,[switch]$Render,[switch]$Encode,[switch]$Open,[string]$Version='v04')
$ErrorActionPreference='Stop'
$ProjectDir=Split-Path $PSScriptRoot -Parent
$BlenderExe=Join-Path $ProjectDir 'tools\blender\blender-5.2.2-windows-x64\blender.exe'
if($Build) {
  & $BlenderExe --background --factory-startup --python-exit-code 1 --python (Join-Path $PSScriptRoot 'build_animatic.py')
  if($LASTEXITCODE -ne 0) {throw 'Animatic build failed'}
  $LatestScene=Get-ChildItem -LiteralPath (Join-Path $ProjectDir 'scenes\versions') -Filter 'trackmesh-v*.blend' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  $Version=$LatestScene.BaseName -replace '^trackmesh-',''
}
$SceneFile=Join-Path $ProjectDir "scenes\versions\trackmesh-$Version.blend"
if($Stills) {
  & $BlenderExe --background $SceneFile --python-exit-code 1 --python (Join-Path $PSScriptRoot 'render_animatic.py') -- --stills-only
  if($LASTEXITCODE -ne 0) {throw 'Animatic still render failed'}
}
if($Render) {
  & $BlenderExe --background $SceneFile --python-exit-code 1 --python (Join-Path $PSScriptRoot 'render_animatic.py')
  if($LASTEXITCODE -ne 0) {throw 'Animatic frame render failed'}
}
if($Encode) {
  python (Join-Path $PSScriptRoot 'encode_animatic.py') --version $Version
  if($LASTEXITCODE -ne 0) {throw 'Animatic encoding failed'}
}
if($Open) {& (Join-Path $PSScriptRoot 'run_hero.ps1') -Open -Version $Version}
