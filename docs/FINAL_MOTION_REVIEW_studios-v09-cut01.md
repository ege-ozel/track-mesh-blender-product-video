# studios-v09 full video — review cut01

Status: Ready for final motion review. Publication is not approved.

- Movie: `D:\CodeSpace\track-mesh-blender-product-video\renders\film\trackmesh-studios-v09-review-cut01.mp4`
- Source: `scenes/versions/trackmesh-studios-v09.blend`
- Duration: 30 seconds; 720 frames; constant 24 fps.
- Resolution: 1920 × 1080.
- Encoding: H.264 High profile, 8-bit yuv420p, MP4.
- File size: 12,846,530 bytes (12.85 MB; 12.25 MiB).
- Audio: No audio track. No music added.
- Existing movie outputs were preserved; a new review filename was selected.

## Validation

1. Saved v09 scene passed `scripts/audit_studios.py` before rendering: 720 frames checked, no failures. Report: `logs/audit-studios-v09.json`.
2. All 720 timeline frames rendered at 100% resolution. Split views were combined into 1920 × 1080 final frames with `scripts/compose_studios.py`.
3. MP4 structure and H.264 SPS inspection passed: 720 samples, 30 seconds, 24 fps, 1920 × 1080, yuv420p, no audio. Report: `logs/probe-trackmesh-studios-v09-review-cut01.json`.
4. Chrome decoded the selected frames and played the full movie to the end without errors or dropped frames. Report: `logs/trackmesh-studios-v09-review-cut01-decoded/verification.json`.
5. Decoded MP4 frames 430 and 690 were visually inspected: captions, Concept visualization, and For Windows are present.

The scene audit does not prove actual product behavior or internet connectivity. This artifact remains subject to final human motion review. No commit, push, upload, or publication was performed.
