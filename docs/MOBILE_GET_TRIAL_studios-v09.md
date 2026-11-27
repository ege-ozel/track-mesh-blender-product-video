# studios-v09 — mobile readability trials

Status: Short alternatives only, pending Claude and human review. Not applied to the full movie; not approved for publication.

## Current Get trial

`renders/film/trackmesh-studios-v09-mobile-get-trial02.mp4`

- Portrait 1080 × 1920, H.264/yuv420p, 24 fps, 261 frames / 10.875 seconds, silent. 1,083,789 bytes.
- Corresponding original interval: frames 300–560 inclusive, 12.4583–23.3333 seconds (end exclusive).
- The selected interval's duration is unchanged. Internal state timing is edited; this is not an observed transfer-speed recording.
- Local frames 1–18: existing Studio B overview, cropped for portrait.
- 19–42: clean existing synthetic app source, Get button and illustrative cursor click.
- 43–198: 6.5-second reconstructed confirmation, reflowed for portrait with the same wording and example data. Illustrative Get click at the end.
- 199–204: 97% for 0.25 seconds; 205–216: 98%; 217–228: 99%; 229–261: existing completed-state capture. No long hold at 97%.
- Example 44 MB / 1.6 GB caption starts with transfer, at local frame 199 / 8.25 seconds. It is not a measured network-total or speed claim.
- Concept visualization is present throughout. The confirmation additionally says Reconstructed confirmation / Not a screen recording. Transfer and completed states say Synthetic state / Timing edited / Not a speed test.

The original confirmation crop was evaluated from decoded MP4 frame 370. Enlarging that crop retains softened text; evidence is `renders/previews/studios-v09-mobile-get-trial01/encoded-crop-quality.png`. It was not used as the main confirmation insert. The sharper insert is a browser reconstruction with portrait text reflow, not a native Windows capture. No privacy-cleared real native confirmation capture was found among the available project assets and capture records.

Current `D:/CodeSpace/track-mesh/apps/desktop/src-tauri/src/receive.rs` was read without modification. It is byte-identical to the v5 source snapshot: SHA-256 `d64142fe18242088fc7f60c3697c7fddd7d430474b679cfc1789b8f458b98d90`. The normal review=true / replace=false branch matches the title, added/changed/removed list, new data and free space, DAW-close and backup text, and Get/Cancel buttons. The example has no executable files; conditional warnings and replacement flows are not demonstrated. Filenames, free space and transfer values remain synthetic.

## Share companion following the additional notes

`renders/film/trackmesh-studios-v09-mobile-share-trial01.mp4`

- 1080 × 1920, H.264/yuv420p, 24 fps, 132 frames / 5.5 seconds, silent. 521,470 bytes.
- Corresponding original interval: frames 97–228, 4.000–9.500 seconds.
- Uses existing v5 native VST3 SDK editor-host captures with synthetic status, over a conceptual DAW backdrop before a simple cut to the plugin. It is labelled as such; it does not prove operation in a real DAW.
- Save precedes the explicit Share current version click. Auto-share stays unchecked. No DAW-close requirement is added to Share; that instruction remains in Get confirmation.
- Static source inserts avoid moving-camera screen resampling and the 3D window-border surface in this short alternative.

## Flicker assessment and quality limits

Consecutive original raw frames 140–151 and 300–311 were inspected after quadrilateral alignment. Contact sheets and pixel-change diagnostics are in `renders/previews/studios-v09-flicker-diagnostic01/`. Differences exist while the underlying UI source is static. Camera sampling, interpolation, lighting and the moving illustrative cursor can contribute; the pixel differences do not independently isolate flicker or prove a product UI problem.

Read-only inspection of the saved scene also found the DAW surface at y=0.201000005 and the plugin-border front at y=0.200999990: effectively coplanar. Depth competition is a plausible border-shimmer cause. It was not isolated with a new render. The original scene and full movie still contain their original imagery; these short alternatives bypass the suspect surfaces rather than repairing the 3D scene.

The plugin source is only 580 × 384 and is enlarged to 960 × 636, so fine text stays soft/pixelated. Enlarged transfer-detail crops also retain raster limitations. The new confirmation is cleaner, but its long body text is about 12 px at a 390 px wide phone preview; reading every line in 6.5 seconds may require pausing. These are editorial review samples, not a guarantee of readability on every phone. No full movie or new 3D frame was rendered.

## Checks and next action

Both current clips passed MP4 structure checks and Chrome playback to the end without errors or dropped frames. Decoded click/transfer/completed frames were visually inspected. Reports:

- `logs/probe-trackmesh-studios-v09-mobile-get-trial02.json`
- `logs/trackmesh-studios-v09-mobile-get-trial02-decoded/verification.json`
- `logs/probe-trackmesh-studios-v09-mobile-share-trial01.json`
- `logs/trackmesh-studios-v09-mobile-share-trial01-decoded/verification.json`
- `logs/studios-v09-temporal-geometry.json`

Original MP4 and studios-v09 blend hashes were checked unchanged against `renders/previews/studios-v09-mobile-get-trial01/original-hashes.json`. Trial01 was preserved when trial02 shortened the transfer hold. Product code was only read, never edited. No commit, push, upload or publication was performed.

Next: Claude reviews the Get and Share alternatives on a phone, including confirmation reading time, softness, cut timing and the tentative flicker diagnosis. Do not apply these edits to the full movie before that review.
