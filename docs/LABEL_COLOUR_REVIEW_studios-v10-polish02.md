# Studio label colour correction — polish02 / GIF v08

Scope: label colour only. Studio A follows the existing PC to PC orange (`#e8aa6e`); Studio B follows the opening teal (`#6ed9c2`). Antialiasing, source codec rounding and GIF palette limits apply at glyph edges. Studio B and the PC to PC labels already have the requested hues in the supplied files, so their pixels were retained.

| File | Duration | Size | Format |
| --- | --- | --- | --- |
| `renders/film/trackmesh-studios-v10-final-16x9-polish02.mp4` | 30 s | 16,633,879 bytes | 1920×1080, 24 fps, H.264, yuv420p, silent |
| `renders/film/trackmesh-studios-v10-final-9x16-polish02.mp4` | 20 s | 9,940,162 bytes | 1080×1920, 24 fps, H.264, yuv420p, silent |
| `renders/readme/trackmesh-flow-v08.gif` | 15.5 s | 4,291,266 bytes | 800×450, 31 frames, infinite loop |

## Exhaustive decoded frame comparison

The specified polish01 MP4s and v07 GIF were used directly. Every frame of each output was decoded and compared to its source, rather than comparing only intermediate composition PNGs.

- Landscape: 720/720 frames checked. Only frames 1–96 changed. Difference bounding box: x=60–195, y=76–97 (zero-based, inclusive). All 624 other frames are completely pixel-identical.
- Portrait: 480/480 frames checked. Only frames 1–30 changed. Same difference bounding box. All 450 other frames are completely pixel-identical.
- GIF: all 31 frames checked. Only indices 0, 1, 2, 3, 28, 29, 30 changed, covering the Studio A hold and its existing dissolves. All differences lie inside x=18–113, y=20–50. All other frames are completely pixel-identical, including the Shared hold (index 4), its dark caption band, and both adjacent transitions on the Shared side.
- **Changed pixels outside label chips: 0 in all three files.** Frame counts, durations, frame order and text are preserved.

The MP4s use lossless H.264 encoding (profile 244, 8-bit YUV420) to preserve the original decoded samples outside the glyph colour patch. This increases their file sizes and may need software decoding on some players. Both played from start to finish in Chrome at normal speed with zero dropped frames and no errors; mobile was displayed at 390 px width. They are not newly compressed delivery copies using the previous lossy High profile.

Source and output BT.709 limited-range matrix metadata match. No new 3D renders or scene/layout edits were made. GIF exterior palette colours were reserved exactly; only glyph pixels were mapped to available palette colours, preserving the existing exterior dithering.

## Evidence

- `logs/label-polish02-16x9.json`: per-frame changed pixel counts, bounds, source/output hashes.
- `logs/label-polish02-9x16.json`: equivalent portrait audit.
- `logs/label-polish02-gif.json`: every GIF frame, duration and Shared-band preservation.
- `logs/probe-trackmesh-studios-v10-final-16x9-polish02.json` and `logs/probe-trackmesh-studios-v10-final-9x16-polish02.json`: passed format checks.
- `logs/trackmesh-studios-v10-final-16x9-polish02-decoded/verification.json` and portrait equivalent: complete normal-speed playback.
- `renders/previews/label-polish02/after-sheet.png`: corrected opening, Studio B and PC to PC samples in both ratios.
- `renders/previews/label-polish02/difference-16x9.png` and portrait equivalent: amplified colour difference maps.

## SHA-256

- `trackmesh-studios-v10-final-16x9-polish02.mp4`: `517ade83aba2d56c2beb3638dd62da4938ee43ed55a19e6a0dbc9dd40a6d242a`
- `trackmesh-studios-v10-final-9x16-polish02.mp4`: `57db443b949f75c2d6c69695111a49e3c432c9b357ca01148a84054a730dfdb6`
- `trackmesh-flow-v08.gif`: `49102455240bb40e76ff77cac70ad7e20d0b1ca6f2dbf20d2fca49aa4c3f9f03`

Original polish01 videos and v07 GIF remain untouched; source hashes were checked again after completion. No product repository changes, commit, push or upload. Ready for review; publication is not approved.
