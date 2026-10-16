# Track Mesh — A+B animatic, 2026-10-13

Scope: only a three-second timing study of the first two shots. The approved disk version v02 is the source; the open v02 window and its unsaved user edits are left untouched.

Scene: `D:/CodeSpace/track-mesh-blender-product-video/scenes/versions/trackmesh-v04.blend`.
V03 preserves the first title-layout draft. V04 reduces the concept label after still-image review. V01/V02 and every previous image remain preserved.

## Timeline

| Time | Frames | Content |
| --- | --- | --- |
| 0.000–1.000 s | 1–24 | Shot A: slow establishing dolly toward the two workstations |
| 1.000–3.000 s | 25–72 | Shot B: cut to left DAW display, followed by gentle approach |
| 1.250–1.667 s | 31–40 | Save observed — illustrative DAW trigger |
| 1.667–2.333 s | 41–56 | Waiting for files to settle — illustrative local preparation |
| 2.333–3.000 s | 57–72 | Snapshot ready — Local snapshot only |

“Concept Visualization” stays visible on every frame. The toast is editable Blender text and plane geometry in front of the illustrative DAW display, not an authentic Track Mesh UI control. The Track Mesh display still uses the original real React capture. No actual save or snapshot command, native API request, receive, transfer, metadata publication, peer connection or application source modification is performed. Save-triggered automation has not been validated in a real DAW; the sequence remains explicitly conceptual.

This is compressed review timing, not the final film's pacing. The intended full storyboard still allocates approximately 4 seconds to establishing and 5 seconds to the DAW shot. There are no particles, packet links, full-film animation or high-resolution renders.

## Files

- Two stills: `D:/CodeSpace/track-mesh-blender-product-video/renders/previews/animatic-v04-A.png` (frame 13) and `D:/CodeSpace/track-mesh-blender-product-video/renders/previews/animatic-v04-B.png` (frame 64).
- Frames: `D:/CodeSpace/track-mesh-blender-product-video/renders/frames/animatic-v04/frame_0001.png` through `frame_0072.png`.
- Completed encoded preview: `D:/CodeSpace/track-mesh-blender-product-video/renders/previews/animatic-v04-3s.webm` (960×540 VP8, 686,312 bytes) and `animatic-v04-3s.gif` (640×360, 6,179,382 bytes).
- Build: `scripts/build_animatic.py`.
- Render: `scripts/render_animatic.py`; existing frames are preserved, enabling safe resumption.
- Encode: `scripts/encode_animatic.py`; refuses to overwrite an encoded preview.
- Scene inspection: `scripts/audit_animatic.py`.
- Launcher: `scripts/run_animatic.ps1`, e.g. `-Open`, `-Stills`, `-Render`, `-Encode`; `-Build` creates the next unused numbered scene from approved v02.
- Browser decoder check: `scripts/verify_animatic_video.cjs`, with representative decoded frames stored under `logs/video-v04-*.png`.

## Validation

- Cycles, 960×540, 16 samples, denoising, 24 fps, frame range 1–72. OptiX RTX 2060 is configured in the rendering process only, with no saved user-preference change.
- Both stills rendered successfully on the GPU and were visually inspected. V03's concept label was too large, so V04 uses a smaller tag outside the monitor. No scene lighting/material/sampling increase.
- All 72 scene frames inspected: correct camera cut at frame 25, exactly one visible concept label, exact three-state visibility without overlap, entire DAW LCD remains inside the close camera's view. Evidence: `logs/animatic-audit-v04.json`.
- The first inspection command had a Python import typo (`blender_extras`); corrected to Blender's built-in `bpy_extras`. Corrected inspection completed successfully; original failed log is retained.
- Existing FFmpeg bundled with Playwright exposes VP8 encoding, but no H.264 encoder. WebM is used for this preview, with no new download or dependency installation. Pillow provides a GIF fallback of the same 72 frames.
- The first encode attempt could not read a PNG sequence: this small FFmpeg has no PNG/image2 input demuxer. The encoder was adapted to a quality-97 MJPEG pipe generated in memory with Pillow. Original PNGs remain untouched. The failed attempt is preserved at `logs/encode-v04-attempt1.log`; corrected encode completed successfully.
- All 72 PNG frames exist. Seventy frames were rendered in the sequence job; frames 13 and 64 reused the reviewed stills. All rendered frames used the GPU; sequence process completed in approximately 6 minutes 12 seconds, including temporary slower frames while Blender windows were open.
- Chrome confirms exactly 3.000 seconds, 960×540, no media errors and playback through the end. HTTP byte-range support and decoded-frame callbacks were added to the local verification server to ensure seeking checks capture the actual target frame rather than a stale video surface. Decoded representative frames at media times 0.500 / 1.417 / 1.958 / 2.667 seconds were visually inspected and show wide / save / settle / ready respectively. Final evidence: `logs/video-verification-v04.json`.
- The GIF contains 72 frames and exactly 3000ms total duration. WebM is the preferred fidelity preview; GIF is a lower-resolution inline fallback. Neither contains audio.
- Disk v02 hash at inspection: `4C7AC6357D941DA0C86EC94681FF76DA95300CE19D3806BE1813BE96E36FFC5E`; disk timestamp remains 2026-10-13 22:50:20 (Europe/Istanbul).

Status: completed. Two stills, all 72 frames, WebM, GIF, scene inspection and decoded video checks succeeded. V04 is open in a visible Blender window. User visual/motion approval is the next gate.

## Commands actually run

From `D:/CodeSpace/track-mesh-blender-product-video`:

```powershell
python -m py_compile .\scripts\build_animatic.py .\scripts\render_animatic.py .\scripts\encode_animatic.py .\scripts\audit_animatic.py
# Run twice: draft v03, smaller concept tag v04
& '.\tools\blender\blender-5.2.2-windows-x64\blender.exe' --background --factory-startup --python-exit-code 1 --python '.\scripts\build_animatic.py'
& '.\tools\blender\blender-5.2.2-windows-x64\blender.exe' --background '.\scenes\versions\trackmesh-v04.blend' --python-exit-code 1 --python '.\scripts\render_animatic.py' -- --stills-only
& '.\tools\blender\blender-5.2.2-windows-x64\blender.exe' --background '.\scenes\versions\trackmesh-v04.blend' --python-exit-code 1 --python '.\scripts\audit_animatic.py'
& '.\scripts\run_hero.ps1' -Open -Version v04
& '.\tools\blender\blender-5.2.2-windows-x64\blender.exe' --background '.\scenes\versions\trackmesh-v04.blend' --python-exit-code 1 --python '.\scripts\render_animatic.py'
python .\scripts\encode_animatic.py --version v04
node .\scripts\verify_animatic_video.cjs v04
```

Next gate: user review of camera cut, approach and concept timing before any longer animation work.
