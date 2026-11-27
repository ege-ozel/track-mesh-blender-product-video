# Claude review: studios-v07, 21 October 2026

Reviewed: `VIDEO_REVIEW_HANDOFF.md`, the nine-shot storyboard, the 1080p frames 370 and 430, the captions in `scripts/compose_studios.py`, and the dialog text in `scripts/capture_demo_ui_v5.cjs`. Compared against the product at `690e6b5` and its `docs/IMPLEMENTATION.md`. Blender was not run, and no file in this project was changed apart from this one.

## Decision (user, 21 October 2026): option (b)

Keep the two studios but take the cities out of the story:

- Place tags: `STUDIO A` and `STUDIO B`, with no city names.
- Shot 3 subtitle: "Another studio." instead of "Another studio, another city."
- Shot 5 stays "PC to PC." with "A direct link. No cloud copy of your project files." The scenes may keep their warm and cool look; just don't name places.
- The 44 MB caption: "Only the changed parts travel. Example: 44 MB new in a 1.6 GB project." (or the same meaning).
- Video description (not on screen): "Windows only. The two PCs connect directly while both are online; at least one of them needs a reachable connection. There is no relay server yet."

## Findings

**P2: the 44 MB / 1.6 GB caption reads as a measurement** (`compose_studios.py` captions, frames 390–450). Same finding as Codex. The numbers come from the demo data, and no transfer was measured. Suggested caption: "Only the changed parts travel. Example: 44 MB new in a 1.6 GB project." Keep it about the data that is new, not a total network byte count.

**P2: Istanbul ↔ Berlin implies transfers over the internet, which have not been checked.** The captions "Another studio, another city." and "PC to PC. A direct link." together tell the viewer that two PCs in different cities connect directly. The product does try that, but the README limits say:
- Transfers between separate networks, behind carrier-grade NAT and across IP changes have not been checked live.
- There is no relay, so the connection may fail when neither PC is reachable.

All live transfers so far ran on one network. Choose one:
- **(a)** Run one real transfer between two different internet connections before publishing, and record it in `IMPLEMENTATION.md`.
- **(b)** Keep the two studios but drop the cities, for example "Another studio." Say the limit in the video description: "PCs connect directly; at least one needs a reachable connection."

**P3: frame 370, the Get window is hard to read.** Same as Codex. The title, the Get/Cancel buttons and the caption read well. The file list and the backup line are small, at an angle and on screen for about 2.3 s. That is fine if the shot only needs to show the flow. If viewers should read the list, hold the shot longer or frame it straighter.

**P3, optional: the closing card.** "Share DAW projects, PC to PC." does not say the app is Windows-only. A small "For Windows" on the end card, or in the description, prevents wrong expectations. Write DAW names only as plain text, without logos (see the trademark note in the README).

## Checked and matching the product

- The Get window matches `receive.rs`:
  - The counts and the `+` / `~` / `−` marks; in the 1080p crop the removed file has `−`.
  - The new data and the free space.
  - "Close this project in your DAW first", the backup and "Open my previous files" text.
  - The Get and Cancel buttons.
  - The old separate "Is the DAW closed?" question is gone.
- The Studio B card reads "Leave project" and "Connected · Studio A", which fits a collaborator who did not create the project.
- The plugin shot:
  - "Share when I save in the DAW" is unchecked, matching the default.
  - Sharing is an explicit click on "Share current version", which fits "One click shares the new version."
- "No cloud copy of your project files" is accurate: the invite service stores encrypted invite drops and hints, never project files.
- No relay, automatic merge or cloud storage is claimed.
- No real invite link, key, PC name or user path is visible. "Studio A/B" and `D:\Music\Neon Forest` are demo values.

## Not covered by this review

- The full animation and the final encode.
- Sound.
- The VST3 in a real DAW.
- Scaled displays.
- Separate networks.

The live rehearsal on the new build (`2d62b1c`, recorded in `IMPLEMENTATION.md`) covered fresh install, invite, approval, first version, Share and Get on one network.
