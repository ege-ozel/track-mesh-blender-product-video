# Hero scene asset provenance

- `assets/backgrounds/studio.png`: byte-for-byte copy of the user-supplied `Sıcak ve Soğuk Işıklı Akustik Stüdyo.png`. Lighting/material reference only. Never loaded onto a backdrop plane. Original authorship/license not independently established; retain user-provided provenance.
- `assets/screens/daw.png`: byte-for-byte copy of user-supplied `Koyu Temalı Profesyonel DAW Düzeni.png`. Illustrative DAW screen, not presented as an authenticated screenshot of Ableton or FL Studio. No monitor frame baked into the image.
- `assets/screens/trackmesh.png`: local browser capture of actual Track Mesh React components and original styles, with a synthetic typed status fixture. No AI-generated product UI. Native calls are replaced only in the isolated demo build. Browser requests outside localhost are blocked during capture.
- `demo-ui/src/{App.tsx,api.ts,styles.css,main.tsx}`: unmodified copies from the user's read-only local repo `D:/CodeSpace/track-mesh/apps/desktop/src`. Hashes recorded in `ui-source-hashes.json`. Repository contains existing uncommitted changes; the copied App reflects those existing local changes, not only the Git commit. No source repo files are modified.
- All studio meshes, desk/monitor/computer/audio-interface meshes, cables and procedural materials are created by `scripts/build_hero_scene.py`. No downloaded models, HDRIs or third-party texture packs.
- Both screen images are packed into the `.blend`; reopening does not require the original paths.

Synthetic DIRECT/CONNECTED/verified-equal values describe an illustrative fixture. They do not establish actual P2P internet reachability or completed end-to-end transfer. Receive remains disabled until explicit DAW-closed consent. No save automation, snapshot transfer animation, particles or guaranteed connection claims are included in this hero.

The supplied starter script is retained as an original artifact and is not run: it contains a photographic background plane, light-link/packet animation and a single shared desk, which conflict with the current hero-only brief.

## A+B concept animatic

`scripts/build_animatic.py` reuses the approved v02 environment and adds two camera motions, editorial concept tags and three illustrative DAW toasts as Blender-native plane/text objects. Text uses Blender's built-in font; no font asset, image, model or plugin is downloaded. DAW-save preparation is labeled Concept Visualization on every frame and never executes real application/native commands. WebM/GIF previews are encoded locally from the 72 rendered PNGs.

## Genuine native VST3 capture

`assets/screens/trackmesh-vst3-native.png` is an actual 580×400 capture of the unmodified compiled TrackMesh VST3 editor in the official SDK editor host. The local SDK is reused under its MIT license, retained beside the project-local host build. User source repo and installed plugin are not modified. The native editor is genuine; displayed project/connection/snapshot data come from a synthetic isolated Named Pipe fixture. `scripts/capture_real_vst3.py` creates and closes only that disposable host and captures only its plugin child window. The texture is packed into v05 and shown during shot B; it is not live VST processing inside Blender. See `NATIVE_VST3_REPORT.md` and `logs/native-vst3-capture.json` for exact binary identity and provenance.
