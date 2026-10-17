# Project Knowledge & Directory Layout: Samurai Edge Demake

This file serves as the canonical map for navigating the repository after the directory cleanup.

## 📁 Directory Structure & File Locations

### 1. Source Code (`src/`)
Contains all production gameplay systems and rendering logic:
- `src/main.py` & root `main.py`: Entry point for launching the game.
- `src/config.py`: Global constants, keybindings, window dimensions, character IDs, and combat tuning.
- `src/entities/`: Character fighters (e.g. `red_samurai.py`, `blue_samurai.py`, `saitou_samurai.py`, `kabuki.py`, `rifleman.py`, etc.), bosses, and projectiles.
- `src/combat/`: Collision detection, damage calculations, hitboxes, and weapon clash mechanics.
- `src/isometric/`: Isometric projection math, camera tracking, and depth sorting.
- `src/world/`: Arena generation, destructible terrain, weather particles, and map data.
- `src/effects/`: Volumetric blood, slicing effects, cinematic director, and particle systems.
- `src/audio/`: Sound manager, dynamic BGM crossfading, and SFX triggers.
- `src/ui/`: Heads-up display, character select grid, arena select carousel, and help screens.
- `src/arcade/`: Arcade mode progression, dialogue system, and score tracking.

### 2. Automated Tests (`tests/`)
All tests reside in `tests/`:
- `tests/test_game.py`: Primary 21-system end-to-end integration test suite.
- Individual feature tests: `test_arcade_mode.py`, `test_arena_engine.py`, `test_clash_qte.py`, `test_demo_edition.py`, etc.
- **Convention**: Test scripts must resolve root with:
  ```python
  ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
  sys.path.insert(0, ROOT)
  ```
- **Running Headless**:
  `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./venv/bin/python tests/test_game.py`

### 3. Developer & Capture Tools (`tools/`)
Utility, generation, and inspection scripts:
- Visual captures: `tools/capture_american_preview.py`, `tools/capture_bakumatsu_preview.py`, `tools/capture_char_select.py`, `tools/capture_ninja_gameplay.py`, `tools/capture_saitou_preview.py`, etc.
- Model & Asset utilities: `tools/model_inspector.py`, `tools/build_hd2d_pilot_sprites.py`, `tools/build_parchment_assets.py`.
- Simulation: `tools/simulate_tournament.py`, `tools/simulate_boss.py`.

### 4. Documentation & Roadmaps (`docs/`)
- **Active Planning & Balance**:
  - `docs/ROADMAP.md` & `docs/ROADMAP_VS_CURRENT_SCOPE.md`: Active project roadmap.
  - `docs/EXPANSION_ROADMAP_AND_DESIGN.md`: Future game expansion specs.
  - `docs/FEEDBACK_FIXES_ROADMAP.md`: Backlog of playtest feedback and fixes.
  - `docs/BALANCE_REPORT*.md`: Character balance analysis (`BALANCE_REPORT.md`, `_easy.md`, `_hard.md`).
  - `docs/GEMINI_MUSIC_PROMPTS.md`: Prompts and reference notes for arena BGM generation.
  - `docs/HANDOFF.md` & `docs/HANDOFF_SDD_EPIC_REFACTOR.md`: Developer handoff instructions.
- **Historical Archive (`docs/archive/`)**:
  - Contains completed sprint summaries (`SPRINT_0_1_COMPLETION_SUMMARY.md`, `SPRINT_2_FINAL_SUMMARY.md`, etc.), phase checklists (`CHECKLIST_FINAL.md`, `PHASE_6_VISUAL_REVAMP.md`), and validation guides (`GUIA_VALIDACAO.md`).
- **Screenshots & Visuals (`docs/screenshots/`)**:
  - Official screenshots and UI previews (`01_title_screen.png`, `char_select_12p_preview.png`, `cinematic_violence_preview.png`, `gameplay_voxel.png`, etc.).

### 5. Assets (`assets/`)
- `assets/sounds/music/`: Active in-game background music tracks (`bgm_*.mp3`).
- `assets/sounds/sfx/`: In-game sound effects.
- `assets/sound_drafts/`: Reference audio drafts and alternative animatic takes (`Song Suggestions/`).
- `assets/Opening Videos/`: Opening video cuts (`Samurai_Edge_Opening_Final.mp4`).
- `assets/portraits/`: Character bust portraits.
- `assets/sprites/`: Character sprite sheets and animations.
- `assets/concepts/`: Concept artwork and visual reference mockups.
- `assets/promotional/`: Store banners, logos, and favicons.

### 6. Deployment & Distribution (`deploy/` & `dist/`)
- `deploy/android/`: Buildozer / Android packaging.
- `deploy/ios/`: Xcode project setup and assets.
- `deploy/itch_assets/`: Storefront assets, description HTML, and upload script (`push_to_itch.sh`).
- `deploy/cors.json`: Cloud storage CORS configuration.
- `dist/releases/`: Standalone packaged binaries (`.zip`, `.tar.gz`).

### 7. Knowledge Base & Specifications (`kb/`)
- `kb/specs/`: Architectural epic specifications (e.g. `vaults-epic.md`, `onboarding-epic.md`, `reconciliation-epic.md`).

### 8. Root Files
- `main.py`: Game entrypoint.
- `README.md`, `CHANGELOG.md`, `LICENSE`: Core project documentation.
- `requirements.txt`: Python package dependencies.
- `samurai_edge.spec` & `buildozer.spec`: PyInstaller and mobile build specs.
- `arcade_save.json`, `settings.json`, `controls_config.json`: Local player saves and configurations (git-ignored).

## 9. 3D Character Aesthetics & Voxel Rendering Directives
- **3D Low-Poly Faceted Anime Architecture (PS1 Era / Tekken 2-3 Inspired)**:
  - **No 2D Decals or Stickers**: Never project flat 2D portraits or decals onto 3D voxel heads.
  - **No Childish Vector Circles**: Never use `pygame.draw.circle` for facial features.
  - **100% Low-Poly 3D Faceted Geometry**: Features must be polygonal prisms, quads, and triangles (protruding 3D nose wedge with directional shading, 3-plane faceted lips with Cupid's bow and specular catchlight).
  - **Luminous Anime Eyes**: Ivory sclera, large vertical iris with vibrant core and dual specular catchlights, crisp winged anime lashline, open lower rim (strictly no orbital under-eye shadow polygons or dark crease lines that cause tired eyes or dark circles).
  - **Delicate Feminine Noses vs Structured Masculine Noses**: Female characters feature slender bridges (~50% width), petite nostril flares, subtle low-poly 3D wedge protrusions, and soft directional shading with a delicate tip specular catchlight. Male characters retain structured, prominent bridges with bolder shadows.
  - **Floating Hair Ribbons & Depth Sorting**: Volumetric floating hair strands, side locks (tsuya-kami), and bangs must be dynamically sorted. Locks on the far side of the head (`is_lock_behind`) must be rendered in `draw_behind` so the cranium solid naturally occludes them, preventing strands from projecting across the face in 3/4 and profile angles. Locks on the camera-facing side render in `draw_head` framing the cheeks, and bangs must stay contoured above the eyebrow line.
  - **Dynamic Depth Sorting (Painter's Algorithm)**: Body parts must be dynamically sorted along the camera depth vector (`depth = rx + ry`). When characters face away from the camera, arms, forearms, and front-held weapons must be rendered *before* the torso and obi so the back of the torso cleanly occludes them, preventing arms from floating on top of the back.
  - **Shinobi Masks, Cowls & Custom Collars**: For characters wearing high collars, ninja suits, balaclavas, or facial masks (e.g. Murasaki, Joe, Kasumi), the jaw frustum (`jaw_color`) and neck box (`neck` in character palette) must inherit the suit or mask fabric color instead of default skin tone. This guarantees no skin cubes or seams bleed through collars, napes, or beneath 3D masks.
  - **Continuous Limbs & Leggings**: Limbs with unbroken garments (kunoichi leggings, tights, hakama) must use continuous 3D tapered mesh ribbons rather than stacked staggered cubes, eliminating knee and elbow joint steps/shelves.
  - **Masculine Martial Eyes vs Luminous Anime Eyes**: Male characters (e.g. Joe, Teppo, Musashi, Saitou, Ren, Benkei, Goro) feature narrower, focused eye apertures with straight, resolute lashlines, compact irises, single sharp specular glints, bold lower brows positioned closer to the eye, and firm un-glossed lips without winged eyeliner flicks or double doe-eyed catchlights. Female characters retain large open sclera, dual glints, and crisp winged lashlines.
  - **Winding Order in Oriented 3D Voxel Boxes**: In `draw_oriented_voxel_box`, all 6 face vertex sets `(p1 - p0) x (p2 - p0)` must point strictly outward to ensure correct 2D screen cross-product back-face culling. If winding is inverted on side faces, weapons (e.g. rifles, katanas) become completely transparent/culled when viewed from profile (90°/270°) angles.
  - **Seam-Free Balaclavas & Cowls**: Jaw frustums connected directly to the cranium must omit their interior top face (`cap_end=False`) to avoid creating a flat horizontal tray/shelf under the face. Solid 3D cheek panels (`mk.obox`) wrap the jaw and temples seamlessly so balaclavas and masks never resemble hollow open boxes.
  - **Back-Gear & Slung Weapons**: Diagonal back-mounted weapons (e.g. tactical katanas, quivers) must stay compact and snug against the assault pack/spine rather than protruding wide past the shoulder into the arm volume.
  - **Pauldron & Shoulder Armor Up-Vector Orientation**: When drawing downward-hanging shoulder armor or ō-sode (e.g. Benkei, Hanzo) with `mk.obox` along direction `sode_dir ≈ (..., ..., -0.95)`, the `up` vector must be explicitly provided as `(fx, fy, 0.0)` rather than default `(0, 0, 1.0)`. Collinear cross-products with Z collapse the orientation matrix, causing pauldrons to swap width with thickness or distort during character rotation.
  - **Sleeve Drape Vectors in 3D Ribbon Meshes**: Sleeves hanging down from shoulder `s` to elbow `e` must use `normal_vec = (fx, fy, 0.0)` (front-to-back thickness) and `side_vec = (px, py, 0.0)` (lateral width). If `normal_vec` is set parallel to the vertical downward spine direction `(0, 0, 1.0)`, cross-products collapse and project horizontal trapezoid wings rather than natural downward-draping kimono sleeves.
  - **Dual-Wielding Weapons & Scabbards Depth Sorting**: Dual-wielding characters (e.g. Musashi) must evaluate the midpoint of both hands `w_mid = ((hand_l[0] + hand_r[0]) * 0.5, (hand_l[1] + hand_r[1]) * 0.5)` against torso depth `d_torso`. When facing away from the camera (`mk.depth(c, w_mid) < d_torso`), both weapons, scabbards, and hands must be drawn in `draw_behind` so the back of the kimono and koshi-ita cleanly occlude them, preventing blades and arms from floating on the character's back.
  - **Headwear, Cavalier Brims & Tricorne Flaps**: Hat brims must maintain a strictly horizontal orientation (`dir_z = 0.0`) sitting safely at or above the forehead/crown line (`crown_z >= hz + 0.145`). If a brim is given downward slope (`dir_z < 0`) towards the camera, the isometric projection compounds the vertical drop with forward screen translation, projecting the brim directly over the eyes like a visor. Upturned brims (e.g. Tricorne front flap, Cavalier cocked brim) along direction `dir ≈ (..., ..., 0.95)` must specify `up = (fx, fy, 0.0)` for front-facing flaps so width expands laterally along `(px, py)` instead of collapsing into a vertical dividing strip.
  - **Oriented Chest Blouses vs Axis-Aligned Boxes**: Front torso garments, open shirts, and collars must use oriented geometry (`mk.obox` along `(0, 0, 1.0)` with `up = (fx, fy, 0.0)`) rather than axis-aligned `cbox` boxes, ensuring lapels and décolletage remain flush against the torso in all 360° camera angles instead of protruding as sharp diagonal corners.
  - **Continuous 3D Ribbon Legs to Boot Cuffs**: When connecting breeches/trousers into bucket-top or cavalier boots, the upper ribbon mesh must extend continuously to the cuff anchor (`spine_points=[top, knee, cuff_pos]`), eliminating blank gaps/shelves before the boot shaft.



