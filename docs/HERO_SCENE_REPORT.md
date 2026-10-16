# Track Mesh — Hero scene delivery, 2026-10-13

Project: `D:/CodeSpace/track-mesh-blender-product-video`.

## Verified environment

- Windows x64, Intel i7-10750H (6 cores / 12 logical processors), NVIDIA RTX 2060.
- Blender **5.2.2 LTS**, official Windows x64 portable ZIP, installed only under this project: `tools/blender/blender-5.2.2-windows-x64/blender.exe`.
- Release source: https://download.blender.org/release/Blender5.2/ . Official manifest: https://download.blender.org/release/Blender5.2/blender-5.2.2.sha256 . ZIP SHA-256 verified as `3849d17a682cba006075aaa3f3597ecb5c9c30ec31035b2e092c53e40679b535`.
- Blender reports build hash `d13f752e3b9c`, Windows, 5.2.2 LTS. Existing `D:/Blender Foundation/Blender 5.0` installation is preserved. Its `--version` was read; no install/addon/preferences change was made there.
- Fresh portable defaults: Eevee engine, Cycles CPU, compute device NONE. Probing detected RTX 2060 OptiX and CUDA. **All six preview renders actually completed on the GPU with OptiX.** HIP and oneAPI have no available device; Metal is unavailable on this platform. The HIP discovery warning does not prevent OptiX renders.
- Blender MCP: no Blender tools exposed in this session, no listener found on default localhost port 9876. Optional MCP setup is not completed. Background Python CLI works; no MCP/addon/client registration was installed or changed.
- Existing Vite/React/Chrome and bundled Playwright/Pillow were reused. No new npm/Python dependency installed, no system-wide changes.

## Scene and image files

- Requested first scene: `D:/CodeSpace/track-mesh-blender-product-video/scenes/versions/trackmesh-v01.blend`.
- Recommended lighting revision: `D:/CodeSpace/track-mesh-blender-product-video/scenes/versions/trackmesh-v02.blend`.
- First previews preserved: `renders/previews/hero-v01-A.png`, `hero-v01-B.png`, `hero-v01-C.png`.
- Recommended previews: `D:/CodeSpace/track-mesh-blender-product-video/renders/previews/hero-v02-A.png` (wide), `hero-v02-B.png` (DAW), `hero-v02-C.png` (Track Mesh).
- UI texture: `D:/CodeSpace/track-mesh-blender-product-video/assets/screens/trackmesh.png`, **1920×1080**, actual unchanged React UI with synthetic data. Source hashes: `docs/ui-source-hashes.json`.
- Scene generator: `scripts/build_hero_scene.py`. Initial code preserved at `scripts/versions/build_hero_scene-v01.py.txt`.
- Render driver: `scripts/render_hero_previews.py`. Environment probe: `scripts/probe_blender.py`.
- Convenience launcher: `scripts/run_hero.ps1`. Visible-process runtime device setup: `scripts/configure_hero_ui.py` (does not save preferences).
- UI build and capture: `scripts/build_demo_ui.mjs`, `scripts/capture_demo_ui.cjs`; fixture: `demo-ui/src/mock-core.ts`.

All scenes contain the same single editable environment, 290 meshes, two separate desks, monitor bevels, independent UV screens, real monitor feet, keyboard keys, mice, speakers, small PCs, audio interfaces, cables, thick acoustic panels, wood slats, floor, solid walls and six named collections. Two PNG screen textures are packed. The background photograph is used only as a visual reference, never as room geometry. Standard desk height is 0.74m and monitor diagonal approximately 34 inches. There are three static perspective cameras, **zero animated objects**, and only frame 1.

## Render and visual review

All stills: **960×540, 16:9, Cycles, 24 samples, denoising**. V01 took approximately 9.11 / 4.29 / 4.35 seconds for A/B/C. V02 took 4.16 / 3.66 / 3.64 seconds. See `logs/renders-v01.json` and `logs/renders-v02.json`.

All six images were visually inspected. The first wide image was too bright for the brief. V02 darkens plaster/walnut/floor, reduces fill light, refines warm/teal lighting and tightens both screen cameras. No samples/resolution increase. Both screen textures are oriented correctly and remain inside the modeled bezels. Desks are visibly separate, with room depth and parallax available for a future camera move. No photographic backdrop, light-link, HUD, packet animation, save automation or full-film render was made.

At 960×540, the wide camera establishes the space; it cannot make small UI labels readable. Close camera C makes the product name, project and main controls visible, but fine UI copy remains small at preview resolution. The real UI asset retains its full 1920×1080 raster. The supplied DAW image is illustrative, not a verified screenshot of a named commercial DAW.

DIRECT, connected and equal-snapshot status are synthetic fixture values; no WAN/P2P reachability or real transfer was verified here. Receive is visibly disabled until DAW-closed consent. Actual source button names are preserved: Share current version / Get collaborator's version. Original source repo, existing source modifications and user files were left unchanged.

Optional refinements for the next approved pass: a slightly more centered wide camera, softer center-wall shadows, and tighter product-screen framing if the supporting text needs emphasis. Visual approval is required before animation or final rendering.

## Commands actually executed

PowerShell from the project root (output logs retained):

```powershell
# Official download, checksum verification, extraction and version read
Invoke-WebRequest -Uri 'https://download.blender.org/release/Blender5.2/blender-5.2.2.sha256' -OutFile '.\tools\blender\blender-5.2.2.sha256'
curl.exe --fail --location --silent --show-error 'https://download.blender.org/release/Blender5.2/blender-5.2.2-windows-x64.zip' --output '.\tools\blender\blender-5.2.2-windows-x64.zip'
Get-FileHash '.\tools\blender\blender-5.2.2-windows-x64.zip' -Algorithm SHA256
Expand-Archive -LiteralPath '.\tools\blender\blender-5.2.2-windows-x64.zip' -DestinationPath '.\tools\blender'
& '.\tools\blender\blender-5.2.2-windows-x64\blender.exe' --version

# Real UI build/capture, with no dependency installation
node .\scripts\build_demo_ui.mjs
node .\scripts\capture_demo_ui.cjs

# Syntax check, device discovery, build (run twice: initial + lighting revision)
python -m py_compile .\scripts\build_hero_scene.py .\scripts\render_hero_previews.py .\scripts\probe_blender.py
& '.\tools\blender\blender-5.2.2-windows-x64\blender.exe' --background --factory-startup --python-exit-code 1 --python '.\scripts\probe_blender.py'
& '.\tools\blender\blender-5.2.2-windows-x64\blender.exe' --background --factory-startup --python-exit-code 1 --python '.\scripts\build_hero_scene.py'

# Each version rendered from the saved blend
& '.\tools\blender\blender-5.2.2-windows-x64\blender.exe' --background '.\scenes\versions\trackmesh-v01.blend' --python-exit-code 1 --python '.\scripts\render_hero_previews.py'
& '.\tools\blender\blender-5.2.2-windows-x64\blender.exe' --background '.\scenes\versions\trackmesh-v02.blend' --python-exit-code 1 --python '.\scripts\render_hero_previews.py'
```

The first scene was also opened using `Start-Process` with the portable Blender executable, `--factory-startup` and the absolute v01 scene path. The final review opens v02 via `scripts/run_hero.ps1 -Open -Version v02`. Existing previews are not overwritten. A later `-Build` creates the next unused version number; `-Preview` refuses to overwrite already-rendered stills.

The original ZIP, top-level setup script, user images, extracted starter files and prior versions are preserved. The supplied setup script was **not** executed. No 30-second animation or final render was attempted.
