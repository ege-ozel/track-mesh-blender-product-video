[CmdletBinding()]
param([switch]$Build, [switch]$Preview, [switch]$Open, [string]$Version='v02')
$ErrorActionPreference='Stop'
$ProjectDir=Split-Path $PSScriptRoot -Parent
$BlenderExe=Join-Path $ProjectDir 'tools\blender\blender-5.2.2-windows-x64\blender.exe'
if(-not (Test-Path -LiteralPath $BlenderExe)) {throw "Blender 5.2.2 not found: $BlenderExe"}
if($Build) {
  & $BlenderExe --background --factory-startup --python-exit-code 1 --python (Join-Path $PSScriptRoot 'build_hero_scene.py')
  if($LASTEXITCODE -ne 0) {throw 'Scene build failed'}
  $LatestScene=Get-ChildItem -LiteralPath (Join-Path $ProjectDir 'scenes\versions') -Filter 'trackmesh-v*.blend' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  $Version=$LatestScene.BaseName -replace '^trackmesh-',''
}
$SceneFile=Join-Path $ProjectDir "scenes\versions\trackmesh-$Version.blend"
if($Preview) {
  & $BlenderExe --background $SceneFile --python-exit-code 1 --python (Join-Path $PSScriptRoot 'render_hero_previews.py')
  if($LASTEXITCODE -ne 0) {throw 'Preview render failed'}
}
if($Open) {Start-Process -FilePath $BlenderExe -ArgumentList @('--factory-startup',('"'+$SceneFile+'"'),'--python',('"'+(Join-Path $PSScriptRoot 'configure_hero_ui.py')+'"')) -WorkingDirectory $ProjectDir}
