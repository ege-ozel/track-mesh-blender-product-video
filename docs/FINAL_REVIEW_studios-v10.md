# studios-v10 — final editorial handoff

Status: Ready for final review, subject to the attached playback checks. Not approved for publication. Product code was not modified. No commit, push, upload or publication was performed.

## Deliverables

- `renders/film/trackmesh-studios-v10-final-16x9.mp4` — 1920 × 1080, 720 frames, 24 fps, 30 seconds, silent H.264/yuv420p.
- `renders/film/trackmesh-studios-v10-final-9x16.mp4` — 1080 × 1920, 480 frames, 24 fps, 20 seconds, silent H.264/yuv420p.
- `renders/readme/trackmesh-flow-v06.gif` — 800 × 450, 7 held moments / 31 encoded frames, 15.5 seconds, infinite loop, below 5 MB.

The requested GIF name `trackmesh-flow-v04.gif` already existed, as did v05. Both were preserved; v06 is the next unused numbered final GIF. Intermediate v10 layout drafts were preserved with `draft01` / `draft02` in their names. Source-film, trial-film, original-blend and existing-GIF hashes are in `logs/studios-v10-protected-inputs.json`.

After final verification, the user requested archiving older videos. Nine superseded MP4/WebM files (including original v09 sources, mobile trials, old film and intermediate v10 video drafts) were moved without deletion to `renders/archive/2026-10-22-pre-v10/`. Its `manifest.json` maps original paths to archived paths and verifies every file's SHA-256 after the move. New v10 final movies and all README GIF versions remain at their output paths. Historical reports retain original source paths; use the archive manifest to locate those videos now.

## Timeline

| Beat | Landscape | Portrait |
| --- | --- | --- |
| Studio A | 0–4.00 s | 0–1.25 s |
| Save | 4.00–4.75 s | 1.25–2.00 s |
| Share current version + illustrative click | 4.75–6.00 s | 2.00–3.00 s |
| Sharing | 6.00–7.00 s | 3.00–3.75 s |
| Shared | 7.00–9.50 s | 3.75–5.25 s |
| Studio B | 9.50–12.50 s | 5.25–6.50 s |
| Card Get + illustrative click | 12.50–13.50 s | 6.50–7.50 s |
| Confirmation + illustrative Get click | 13.50–19.00 s | 7.50–12.50 s |
| Transfer | 19.00–20.00 s | 12.50–13.50 s |
| Got Studio A's version ✓ | 20.00–22.50 s | 13.50–16.00 s |
| PC to PC | 22.50–26.00 s | 16.00–18.00 s |
| TrackMesh / For Windows | 26.00–30.00 s | 18.00–20.00 s |

The Example caption starts on the first transfer frame and remains through completion: 3.5 seconds in each format. The 97% state lasts 6 frames / 0.25 seconds, followed by 98% and 99%, then 2.5 seconds of readable completion. In this synthetic example the whole-project percentage starts high because data is reused; this is not a general claim about every download. Values match `demo-ui-v5/mock-core.ts`: total 1,717,986,918 bytes and remaining states 46,137,344 / 30,408,704 / 11,534,336 bytes, displayed as 44.0 / 29.0 / 11.0 MB and 97 / 98 / 99 percent. Edit timing does not measure transfer speed.

## What was regenerated

No full 3D movie was rendered again. The edit reuses the existing v09 atmosphere frames, static completed-state split-camera views and clean v5 UI sources. The earlier Get and Share trials supplied the editorial approach; their trial labels and duplicated progress presentation were removed. Each aspect ratio has its own layout and frame sequence.

Share now uses static clean VST3 captures over a conceptual DAW backdrop, with distinct Save / Share / Sharing / Shared headings. Cursor presses are illustrative. The low-resolution render crop was not enlarged to recover detail. Both studio atmospheres and Studio A/B labels remain. Desktop Get, transfer and completion were reflowed into single clean closeups; there is only one progress bar. The exact approved confirmation title, body, filenames, quantities and Get/Cancel labels were retained. Current `receive.rs` was read only; its SHA-256 still matches the v5 copied source. These are reconstructed UI presentations, not native Windows or real DAW evidence.

The portrait PC-to-PC view places Studio A above Studio B. PC-to-PC and end-card backgrounds are held still instead of continuing the original outro camera move; this avoids moving-window/key shimmer in those sections. No transfer packets continue moving after completion.

## Flicker findings, with limits

The original render issue is not presented as a product defect. Existing consecutive-frame inspection and mesh coordinates identify plausible contributors: moving-camera sampling of thin high-contrast edges and an effectively coplanar plugin-border front / DAW plane (y≈0.201).

Six new diagnostic 1080p stills were rendered from the saved v09 scene only: three with the camera fixed at frames 140–142, then three with only the border moved 0.004 scene units away. The source blend was not saved or changed. Fixed-camera adjacent differences were at most 1/255 per channel in both variants. Separating the border changed 9,650 pixels in the frame, with mean absolute difference ≈0.020/255 over the whole image.

**These results are clues, not proof of the sole flicker cause.** Three fixed-camera frames do not establish temporal behavior under camera motion, and there was no independent sampling-only comparison. Depth competition and thin-edge sampling cannot be conclusively apportioned from this diagnostic. Further 3D experiments were unnecessary for this edit because the affected moving 3D Share panel is replaced with stable clean source inserts. The rest of the movie was not rerendered.

Evidence: `renders/previews/studios-v10-flicker-diagnostic/manifest.json` and `comparison.json`; the six images are retained alongside them.

## Quality limits

- Native VST3 input is 580 × 384. Its current source scales from the host monitor DPI at attachment, with no live DPI-change handler or independent high-resolution capture option identified in the existing host. No system DPI setting, binary or product source was changed to manufacture a larger capture. Enlarging this bitmap does not add detail; fine plugin text remains softer than the newly reflowed UI. The phase headings and separate source-wording status caption remain readable.
- At approximately 390 px display width, the Get list and primary controls are readable; reading every word of the long confirmation within five seconds may still require pausing. The confirmation was lengthened rather than shortened relative to the original film. Completion is shown as the large actual Got status, not a small card beside a duplicate bar.
- Atmosphere shots retain their original rendering and sampling texture. The edit avoids the diagnosed Share-edge region and freezes the optional outro movement; it does not claim every original 3D detail was repaired.
- GIF uses per-frame palettes and dithering to reduce banding where practical, with clean caption/disclosure lettering prioritized. GIF's color limit can still leave grain or tonal steps; no zero-banding guarantee is made.

## Review evidence

Both encoded movies are independently probed for dimensions, sample count, duration, frame rate, H.264 and 8-bit yuv420p, with no audio track. Each is played from beginning to end at playbackRate=1. The portrait player is 390 px wide. Normal-speed playback samples every approximately 0.5 seconds and the cut/click boundary seeks are retained in each decoded log folder; visual contact sheets were reviewed.

- `logs/probe-trackmesh-studios-v10-final-16x9.json`
- `logs/probe-trackmesh-studios-v10-final-9x16.json`
- `logs/trackmesh-studios-v10-final-16x9-decoded/verification.json`
- `logs/trackmesh-studios-v10-final-9x16-decoded/verification.json`
- Each decoded folder's `normal-speed-contact.png` and `normal-speed/` images.
- `renders/readme/trackmesh-flow-v06.json` and `trackmesh-flow-v06-storyboard.png`.

The horizontal layout was corrected after playback review to separate the PC-to-PC title, subtitle and disclosure footer and preserve the confirmation's full lower edge. Its final encode and playback checks were repeated after those changes; earlier review material is retained under `draft01` / `draft02`.

English/Turkish explanation text, including synthetic status, reconstruction, Windows/reachability limits and timing qualifications, is in `docs/VIDEO_DESCRIPTION_studios-v10.md`. Next action: Claude and the user review the final motion and GIF; do not treat file creation as publication approval.
