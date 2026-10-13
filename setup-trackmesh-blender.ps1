# Track Mesh cinematic Blender starter - Windows PowerShell 5.1 / 7
# Review this file before executing: downloads official Blender ZIP and installs Blender MCP from PyPI.
[CmdletBinding()]
param(
    [string]$ProjectRoot = (Join-Path $HOME 'TrackMeshVideo'),
    [switch]$SkipBlenderDownload,
    [switch]$SkipMcp,
    [switch]$SkipPreview
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Version = '5.2.2'
$ZipName = "blender-$Version-windows-x64.zip"
$BlenderUrl = "https://download.blender.org/release/Blender5.2/$ZipName"
# Checksum of official Blender Foundation 5.2.2 Windows x64 portable ZIP.
$BlenderSha256 = '3849d17a682cba006075aaa3f3597ecb5c9c30ec31035b2e092c53e40679b535'
$McpPackage = 'blender-mcp==1.9.0'
$BlenderHome = Join-Path $HOME 'TrackMeshBlenderTools'
$BlenderExe = Join-Path $BlenderHome "blender-$Version-windows-x64\blender.exe"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Definition

function Step([string]$Label) { Write-Host "`n==== $Label ====" -ForegroundColor Cyan }
function New-Directory([string]$Path) { if (-not (Test-Path -LiteralPath $Path)) { $null = New-Item -ItemType Directory -Path $Path -Force } }
function Copy-Template([string]$Source, [string]$Dest) {
    if (-not (Test-Path -LiteralPath $Source)) { throw "Kit file missing: $Source" }
    if (-not (Test-Path -LiteralPath $Dest)) { Copy-Item -LiteralPath $Source -Destination $Dest }
    else { Write-Host "Preserved existing file: $Dest" }
}
function Find-Exe([string]$Name) {
    $item = Get-Command $Name -ErrorAction SilentlyContinue
    if ($null -ne $item) { return $item.Source }
    return $null
}
function Run-Checked([string]$Exe, [string[]]$Arguments) {
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed ($LASTEXITCODE): $Exe $($Arguments -join ' ')" }
}

Step '0/7 - Environment / folders'
if ($PSVersionTable.PSEdition -eq 'Core' -and -not $IsWindows) { throw 'This setup requires Windows.' }
if (-not [Environment]::Is64BitOperatingSystem) { throw 'This kit targets Windows x64.' }
New-Directory $ProjectRoot
foreach ($p in @('assets\backgrounds','assets\screens','assets\models','scripts','scenes','renders\previews','renders\frames','docs')) {
    New-Directory (Join-Path $ProjectRoot $p)
}
Copy-Template (Join-Path $Here 'scripts\build_scene.py') (Join-Path $ProjectRoot 'scripts\build_scene.py')
Copy-Template (Join-Path $Here 'docs\TRACKMESH_VIDEO_MASTER_PROMPT.md') (Join-Path $ProjectRoot 'docs\TRACKMESH_VIDEO_MASTER_PROMPT.md')
Copy-Template (Join-Path $Here 'docs\GORSEL_URETIM_PROMPTLARI.md') (Join-Path $ProjectRoot 'docs\GORSEL_URETIM_PROMPTLARI.md')
Copy-Template (Join-Path $Here 'docs\README_KURULUM.md') (Join-Path $ProjectRoot 'README_KURULUM.md')
Write-Host "Project: $ProjectRoot"

Step '1/7 - Blender 5.2.2 portable installation'
if (-not (Test-Path -LiteralPath $BlenderExe)) {
    if ($SkipBlenderDownload) {
        Write-Warning "Blender not found at $BlenderExe. Skipping installation as requested."
    } else {
        New-Directory $BlenderHome
        $zip = Join-Path $BlenderHome $ZipName
        if (Test-Path -LiteralPath $zip) {
            $hash = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant()
            if ($hash -ne $BlenderSha256) { Remove-Item -LiteralPath $zip -Force }
        }
        if (-not (Test-Path -LiteralPath $zip)) {
            Write-Host 'Downloading ~386 MiB from blender.org. This may take several minutes...'
            Invoke-WebRequest -Uri $BlenderUrl -OutFile $zip -MaximumRedirection 5
        }
        $hash = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($hash -ne $BlenderSha256) { throw "Blender SHA256 mismatch. Expected $BlenderSha256, got $hash. Do not run this ZIP." }
        Write-Host 'Verified Blender ZIP SHA256.' -ForegroundColor Green
        Expand-Archive -LiteralPath $zip -DestinationPath $BlenderHome -Force
        if (-not (Test-Path -LiteralPath $BlenderExe)) { throw "Blender executable not found after extraction: $BlenderExe" }
    }
}
if (Test-Path -LiteralPath $BlenderExe) {
    Run-Checked $BlenderExe @('--version')
} else {
    Write-Warning 'Blender portable executable unavailable; scene build will be skipped.'
}

Step '2/7 - uv / uvx package manager'
$UvX = Find-Exe 'uvx'
if (-not $UvX) {
    $localUv = Join-Path $HOME '.local\bin\uvx.exe'
    if (Test-Path -LiteralPath $localUv) { $UvX = $localUv }
}
if (-not $SkipMcp -and -not $UvX) {
    $winget = Find-Exe 'winget'
    if (-not $winget) {
        Write-Warning 'winget not found. Install uv manually from https://docs.astral.sh/uv/getting-started/installation/ and rerun.'
    } else {
        Write-Host 'Installing uv via winget...'
        & $winget install --id astral-sh.uv --exact --accept-source-agreements --accept-package-agreements
        if ($LASTEXITCODE -ne 0) { Write-Warning 'winget failed or was cancelled; uv installation remains incomplete.' }
    }
    $UvX = Find-Exe 'uvx'
    if (-not $UvX -and (Test-Path -LiteralPath $localUv)) { $UvX = $localUv }
    if (-not $UvX) {
        $found = Get-ChildItem -Path (Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Links') -Filter 'uvx.exe' -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) { $UvX = $found.FullName }
    }
}

Step '3/7 - Blender MCP add-on'
if (-not $SkipMcp -and $UvX) {
    Write-Host "Using uvx: $UvX"
    $oldOverride = $env:BLENDERMCP_ADDONS_DIR
    try {
        # Target Blender 5.2 specifically; leave 5.0 add-ons untouched.
        $env:BLENDERMCP_ADDONS_DIR = Join-Path $env:APPDATA 'Blender Foundation\Blender\5.2\scripts\addons'
        New-Directory $env:BLENDERMCP_ADDONS_DIR
        Run-Checked $UvX @('--python','3.11','--from',$McpPackage,'blender-mcp','install-addon')
    } finally {
        $env:BLENDERMCP_ADDONS_DIR = $oldOverride
    }
} elseif ($SkipMcp) {
    Write-Host 'MCP install skipped by parameter.'
} else {
    Write-Warning 'uvx missing; MCP add-on not installed.'
}

Step '4/7 - Register MCP with installed CLI clients'
if (-not $SkipMcp -and $UvX) {
    $claude = Find-Exe 'claude'
    $codex = Find-Exe 'codex'
    if ($claude) {
        Write-Host 'Configuring Claude Code MCP...'
        $listing = (& $claude mcp list 2>&1 | Out-String)
        if ($listing -match '(?m)^blender\b|\bblender:') {
            Write-Host 'Claude Code blender MCP already registered; preserved.'
        } else {
            & $claude mcp add --scope user blender -- $UvX --python 3.11 --from $McpPackage blender-mcp
            if ($LASTEXITCODE -ne 0) { Write-Warning 'Claude MCP setup failed; configure it manually.' }
        }
    } else { Write-Warning 'Claude Code CLI not found; account-dependent installation skipped.' }
    if ($codex) {
        Write-Host 'Configuring Codex MCP...'
        $listing = (& $codex mcp list 2>&1 | Out-String)
        if ($listing -match '(?m)^blender\s|\bblender\b.*blender-mcp') {
            Write-Host 'Codex blender MCP already registered; preserved.'
        } else {
            & $codex mcp add blender -- $UvX --python 3.11 --from $McpPackage blender-mcp
            if ($LASTEXITCODE -ne 0) { Write-Warning 'Codex MCP setup failed; configure it manually.' }
        }
    } else { Write-Warning 'Codex CLI not found; account-dependent installation skipped.' }
} else { Write-Host 'MCP client registration skipped.' }

Step '5/7 - Generate 3D proof-of-concept (.blend)'
if (Test-Path -LiteralPath $BlenderExe) {
    $sceneFile = Join-Path $ProjectRoot 'scenes\trackmesh-starter.blend'
    if (-not (Test-Path -LiteralPath $sceneFile)) {
        $previous = $env:TRACKMESH_VIDEO_PROJECT
        $env:TRACKMESH_VIDEO_PROJECT = $ProjectRoot
        try {
            $args = @('--background','--factory-startup','--python',(Join-Path $ProjectRoot 'scripts\build_scene.py'))
            if (-not $SkipPreview) { $args += @('--','--preview') }
            Run-Checked $BlenderExe $args
        } finally { $env:TRACKMESH_VIDEO_PROJECT = $previous }
    } else {
        Write-Host "Preserved existing Blender scene: $sceneFile"
    }
}

Step '6/7 - Optional asset folders'
Write-Host 'Add only non-sensitive, fictional UI images to:'
Write-Host (Join-Path $ProjectRoot 'assets\screens\daw.png')
Write-Host (Join-Path $ProjectRoot 'assets\screens\trackmesh.png')
Write-Host (Join-Path $ProjectRoot 'assets\backgrounds\studio.png')
Write-Host 'The starter scene works without these images; rerun build_scene.py via Blender after adding them.'

Step '7/7 - Wrap-up'
Write-Host "`nSetup complete (check warnings above)." -ForegroundColor Green
Write-Host "Project: $ProjectRoot"
Write-Host "Blender: $BlenderExe"
Write-Host "Master prompt: $(Join-Path $ProjectRoot 'docs\TRACKMESH_VIDEO_MASTER_PROMPT.md')"
Write-Host 'ONE MANUAL STEP REMAINS: Open Blender 5.2 -> Edit > Preferences > Add-ons -> enable Blender MCP;'
Write-Host 'then in the 3D View press N -> BlenderMCP -> Start MCP Server (or Connect to Claude).'
Write-Host 'Restart Claude Code/Codex after MCP registration. Use only one MCP client connection at once.'
