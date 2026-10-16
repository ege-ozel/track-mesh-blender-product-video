# Real TrackMesh VST3 visual revision — 2026-10-13

User approved the A+B animatic's camera tempo, requested the real TrackMesh VST3, chose its native window on the existing Blender DAW screen with synthetic demo data, and deferred moving the DAW arrangement.

## Actual plugin and capture

The **unmodified compiled native VST3** was loaded by the official Steinberg SDK editor host. This is not a recreated HTML/GDI lookalike, source-only rendering or AI-generated UI.

- Binary read: `D:/CodeSpace/track-mesh/.build/vst3/VST3/Release/TrackMesh.vst3/Contents/x86_64-win/TrackMesh.vst3`.
- SHA-256 before and after capture: `e652aac60885cd6cbe22099dbe31d8c640ce874b3470624de0a200b691bbe8be`.
- Native child window class: `TrackMeshVST3View-v1`.
- Actual native client capture: `D:/CodeSpace/track-mesh-blender-product-video/assets/screens/trackmesh-vst3-native.png`, **580×400**. Windows PrintWindow captured only the newly created plugin child window, never the user desktop or other applications.
- SDK editor host built at `tools/vst3-editorhost/bin/editorhost.exe` using the existing official local SDK, existing MSVC/CMake/Ninja, and a new build directory inside the video project. Target `editorhost` only; no validator, test suite or plugin rebuild. No dependency download/install.
- SDK license is MIT; existing local SDK LICENSE retained at `tools/vst3-editorhost/Steinberg-SDK-LICENSE.txt`.
- A process-specific unique Named Pipe suffix, current-user-only DACL and remote-client rejection isolated the synthetic status fixture. The real Rust agent/desktop was prevented from launching by a nonexistent owner path, and an isolated unused data-directory override was set only in that host process's environment. No production profiles, DBs, invitations, identities or peer/network session were read or opened.
- Fixture displays Neon Forest Demo, Studio B, synthetic local/remote heads and DIRECT as demo values. The random displayed project UUID belongs to this freshly created disposable plugin instance. No real project is linked. Receive remains disabled. No send/receive action is run; recorded events are PLUGIN_CONNECTED and GET_STATUS only.
- The capture process closes only its own editor-host window. Other DAWs and Blender windows are not closed or modified.
- Evidence: `logs/native-vst3-capture.json` and `logs/build-vst3-editorhost.log`.

The separately installed `C:/Program Files/Common Files/VST3/TrackMesh.vst3` has a different hash. It was read for identification only and left untouched. The bundled build above is the exact genuine plugin used in this capture.

## Scene revision

- New scene: `D:/CodeSpace/track-mesh-blender-product-video/scenes/versions/trackmesh-v05.blend`.
- Build code: `scripts/build_vst3_animatic.py`.
- Stills: `renders/previews/animatic-v05-A.png` and `animatic-v05-B.png`.
- PNG sequence: `renders/frames/animatic-v05/frame_0001.png` through `frame_0072.png`.
- Completed video: `D:/CodeSpace/track-mesh-blender-product-video/renders/previews/animatic-v05-3s.webm`, VP8, 960×540, exactly 3 seconds, 686,073 bytes.
- Completed inline fallback: `D:/CodeSpace/track-mesh-blender-product-video/renders/previews/animatic-v05-3s.gif`, 640×360, 72 frames, exactly 3000ms.

The 580×400 native capture is packed into the blend and mapped onto an independent screen-local floating-window mesh inside the existing DAW monitor. It is revealed at the shot-B cut, frame 25, and stays visible through frame 72. The existing illustrative DAW arrangement remains static. The genuine TrackMesh React capture on the other monitor remains unchanged.

The native UI is a captured image in Blender, not a live VST/audio host inside Blender. It was obtained by actually loading and displaying the real VST3. The chosen synthetic IPC fixture is presentation data, not proof of actual snapshot creation, DAW-save automation, verified peer equality, internet reachability or file transfer.

The native popup remains above the three editorial concept toasts, with no fake controls added to its actual interface. Concept Visualization is still visible on every frame. Save preparation stays explicitly conceptual, and snapshot creation is still distinct from file transmission.

## Checks

- Camera cut, positions, rotations and lens values match approved v04 exactly at all **72 frames**. `scripts/audit_vst3_motion.py` verifies these independently without saving either file.
- All 72 frames pass concept-label/state visibility and LCD/native-popup framing checks. `logs/animatic-audit-v05.json` and `logs/native-motion-trackmesh-v05.json` hold evidence.
- Two 960×540 Cycles stills rendered on OptiX, 16 samples, denoising, and were visually inspected. Actual native Send Snapshot / Receive UI is present and fits the LCD.
- Shot A's 24 PNGs are reused exactly from approved v04, because the VST3 popup is hidden for those frames. Only shot B was re-rendered; the reviewed frame 64 is reused as well. Exactly 47 new sequence frames rendered successfully with OptiX in approximately 3 minutes 1 second. Final sequence has all 72 PNGs.
- WebM/GIF encoding succeeded with existing FFmpeg/Pillow. Chrome decoded the 960×540 WebM, confirmed its 3-second duration and reached playback end. Actual presented-frame callbacks and canvas captures verify the visible native VST3 at save/settle/ready timestamps. The encoded ready frame was visually inspected. Evidence: `logs/encoded-v05.json`, `logs/video-verification-v05.json`, `logs/video-v05-*.png`.
- Final byte comparison confirms all 24 reused wide frames are identical to v04, the compiled VST3 SHA-256 is unchanged, and both media previews exist. V05 is open in a visible Blender window; the prior open v04 was preserved.
- Original source repo and installed plugin remain read-only; all scene changes/new build outputs live in the video project. Original images and prior blend/preview versions are preserved.

Status: complete. Native capture, scene, two stills, 72 PNGs, WebM/GIF, camera comparison and decoded video checks succeeded. VST3 placement is ready for user visual review.

## Commands executed

From the video project root:

```powershell
.\scripts\build_vst3_editorhost.cmd
python .\scripts\capture_real_vst3.py
& '.\tools\blender\blender-5.2.2-windows-x64\blender.exe' --background --factory-startup --python-exit-code 1 --python '.\scripts\build_vst3_animatic.py'
& '.\tools\blender\blender-5.2.2-windows-x64\blender.exe' --background '.\scenes\versions\trackmesh-v05.blend' --python-exit-code 1 --python '.\scripts\render_animatic.py' -- --stills-only
& '.\tools\blender\blender-5.2.2-windows-x64\blender.exe' --background '.\scenes\versions\trackmesh-v05.blend' --python-exit-code 1 --python '.\scripts\audit_animatic.py'
& '.\tools\blender\blender-5.2.2-windows-x64\blender.exe' --background '.\scenes\versions\trackmesh-v05.blend' --python-exit-code 1 --python '.\scripts\audit_vst3_motion.py'
& '.\tools\blender\blender-5.2.2-windows-x64\blender.exe' --background '.\scenes\versions\trackmesh-v05.blend' --python-exit-code 1 --python '.\scripts\render_animatic.py'
python .\scripts\encode_animatic.py --version v05
node .\scripts\verify_animatic_video.cjs v05
& '.\scripts\run_hero.ps1' -Open -Version v05
```

Next gate: review the actual VST3 placement/readability; preserve approved tempo. Real DAW compatibility/save behavior would require separate explicit validation in an isolated real DAW project and is not claimed by this screen capture.
