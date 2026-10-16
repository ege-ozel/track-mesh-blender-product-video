# Isolated Track Mesh screenshot environment

Original `App.tsx`, `api.ts`, `styles.css` and `main.tsx` are copied unchanged. Vite aliases only `@tauri-apps/api/core` to `src/mock-core.ts`. The mock answers `get_status` using synthetic values and rejects other commands. There is no native process, filesystem, invitation payload, real identity, secret, database or real peer.

Build: `node scripts/build_demo_ui.mjs` from the video project root. It reuses existing Vite/React dependencies from the read-only Track Mesh checkout (override with `TRACKMESH_SOURCE`). No packages are installed.

Capture: `node scripts/capture_demo_ui.cjs`. Uses bundled Playwright and installed Chrome in a separate headless context; serves only the built demo on a temporary localhost port, blocks external requests, takes a 1920×1080 PNG and closes browser/server. A 1536×864 CSS viewport at 1.25 device scale is used to keep the real UI readable. It refuses to overwrite an existing screenshot.

Fixture state is illustrative: Studio A, Studio B, Neon Forest Demo, EQUAL snapshot lineage and DIRECT QUIC. No actions are performed and no actual transfer or network verification is claimed. Displayed controls retain the original current product names, including `Share current version` and `Get collaborator's version`.
