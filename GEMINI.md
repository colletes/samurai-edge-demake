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
- Active feature suites: `test_arcade_mode.py` (12 fights ladder), `test_boss_oni.py`, `test_cycle6_full_integration.py`, `test_cycle6_combat.py`, `test_cycle6_arenas.py`, `test_demo_edition.py`, `test_translation_and_ui.py`, `test_language_setting.py`, `test_parchment_screens.py`, `test_opening_video.py`, `test_seimei_rondel.py`, `test_audio_system.py`, `test_controllers_and_touch.py`.
- **Convention**: Test scripts must resolve root with:
  ```python
  ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
  sys.path.insert(0, ROOT)
  ```
- **Running Headless**:
  `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./venv/bin/python tests/test_game.py`

### 3. Developer & Capture Tools (`tools/`)
Utility, generation, and inspection scripts:
- Model & Asset utilities: `tools/studio_inspector.py` (Unified 3D Studio: Models F1, Arenas F2, Staging F3), `tools/model_inspector.py`, `tools/arena_inspector.py`, `tools/build_hd2d_pilot_sprites.py`, `tools/build_parchment_assets.py`.
- Simulation & Generators: `tools/generate_arcade_tables.py`, `tools/simulate_tournament.py`, `tools/simulate_boss.py`, `tools/generate_itch_promotional_assets.py`.

### 4. Documentation & Roadmaps (`docs/`)
- **Active Planning & Specs**:
  - `docs/ROADMAP.md`: Active project roadmap.
  - `docs/EXPANSION_ROADMAP_AND_DESIGN.md`: Canonical master roadmap and expansion specs for the 24 fighters.
  - `docs/GEMINI_MUSIC_PROMPTS.md`: Prompts and reference notes for arena BGM generation.
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

### 7. Root Files
- `main.py`: Game entrypoint.
- `README.md`, `CHANGELOG.md`, `LICENSE`: Core project documentation.
- `requirements.txt`: Python package dependencies.
- `samurai_edge.spec` & `buildozer.spec`: PyInstaller and mobile build specs.
- `arcade_save.json`, `settings.json`, `controls_config.json`: Local player saves and configurations (git-ignored).

## 8. 3D Character Aesthetics & Voxel Rendering Directives
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
  - **Model Viewer & Inspector Synchronization**: Whenever a new character model is created or updated, ALWAYS immediately register and synchronize the new combatants in the 3D Model Inspector (`tools/model_inspector.py`) and the in-game help manual (`src/ui/game_help.py`), ensuring they appear in the roster catalog, HUD cards, pedestals, and interactive orbital 3D viewer.

## 9. 2D Rendering, UI, Text & Font Transparency Directives (Zero Artifacts Policy)
Whenever implementing UI elements, banners, floating combat callouts, or cinematic overlays with text:
- **STRICT PROHIBITION: Never call `.set_alpha()` on `pygame.SRCALPHA` Surfaces or Font Surfaces**:
  - In Pygame and SDL2, `font.render(text, True, color)` produces an `SRCALPHA` surface where transparent pixels retain the text's RGB values with `A=0`.
  - Calling `surface.set_alpha(alpha)` on a surface with per-pixel alpha destroys the per-pixel alpha flag in SDL2 software blits, treating the background's `A=0` as opaque pixels modulated by surface alpha. This causes the infamous "font highlight box" bug (opaque white/black rectangular boxes around text and Kanji overlays).
- **The Golden Rule for Alpha / Fading on Per-Pixel Alpha Surfaces**:
  - Always fade surfaces with per-pixel alpha using `special_flags=pygame.BLEND_RGBA_MULT`:
    ```python
    if alpha < 255:
        fade_mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        fade_mask.fill((255, 255, 255, max(0, min(255, alpha))))
        surf.blit(fade_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    ```
- **Zero Uninitialized Alpha Buffers**:
  - Every freshly allocated `pygame.Surface((w, h), pygame.SRCALPHA)` intended as a composite canvas must immediately execute `surf.fill((0, 0, 0, 0))` before drawing shapes or blitting text onto it.
- **Cinematic & Kanji Overlays**:
  - All cinematic banners (`_build_kanji_overlay`), round announcements (`準備 / 始め`), victory banners, and combat callouts must use `BLEND_RGBA_MULT` for alpha fading. Never mutate cached source surfaces with `set_alpha()`.
- **Automated Verification**:
  - Keep `tests/test_font_transparency.py` passing 100% to ensure no text bounding boxes or opaque artifacts regress.
Whenever implementing new features, UI screens, combat systems, or asset additions, ALWAYS consider iOS compatibility:
- **Strict Case-Sensitivity on APFS**: The physical iOS filesystem is strictly case-sensitive. All asset paths, filenames, and extensions must match the exact disk casing (e.g. `.png` vs `.PNG`, `assets/sounds/` vs `assets/Sounds/`).
- **Path Resolution**: Never use hardcoded desktop machine paths (`/Users/...`, `C:\...`). Always use relative paths from the project root or resolve dynamically via `os.path.join(os.path.dirname(__file__), ...)`.
- **Touch & Controller Support**:
  - The game supports MFi / Bluetooth controllers (ExtendedGamepad) and touch events (`FINGERDOWN`, `FINGERUP`, `FINGERMOTION` / virtual controls).
  - Desktop-specific SDL flags (like disabling `SDL_JOYSTICK_MFI`) must NEVER execute on iOS. Always guard with `if sys.platform == "darwin" and os.environ.get("KIVY_BUILD") != "ios":`.
- **Orientation & Safe Area (Notch / Dynamic Island)**:
  - The game is fixed to Landscape (`UIInterfaceOrientationLandscapeLeft` / `UIInterfaceOrientationLandscapeRight`).
  - HUD elements, lifebars, and pause buttons must respect screen margins and safe area insets so they are not obscured by the Dynamic Island or Home indicator.
- **Graceful Dependency Fallbacks**:
  - Any desktop-only or optional libraries (e.g. `pyvidplayer2`, `opencv`, debug profilers) MUST be wrapped in `try/except ImportError` with seamless gameplay fallbacks so the game runs smoothly even if a module is absent.
- **Mobile Memory & Rendering Efficiency**:
  - Avoid allocating new `pygame.Surface` instances every frame inside the main game loop; cache and reuse surfaces to maintain a rock-solid 60 FPS on mobile chips.
- **Xcode Project Synchronization**:
  - Any changes to `assets/`, `src/`, or root configs must be synced to the iOS Xcode project using `deploy/ios/sync_game_to_xcode.sh`.

## 11. Release Packaging & Lightweight Asset Hygiene Directives (All Platforms)
Whenever preparing, building, or packaging production release archives (`.zip`, `.tar.gz`, `.apk`, `.ipa`, installer) for ANY platform (macOS, Windows, Linux, Android, iOS):
- **Strict Runtime-Only Asset Packaging**:
  Never blindly copy or bundle the entire `assets/` directory. All builds must strictly exclude non-runtime development, draft, and marketing assets:
  - `assets/sound_drafts/`: Reference audio drafts, discarded song suggestions, animatic stems (save >110 MB).
  - `assets/Opening Videos/Take *`: Intermediate raw AI video takes. Only `Samurai_Edge_Opening_Final.mp4` belongs in production builds (save >55 MB).
  - `assets/concepts/HD2D_Concept_Art.pdf` & `*_gameplay_mockup.jpg`: Art pitch documents and Photoshop design mockups. Only active in-game concepts (`sumie_title_logo_concept.jpg`, arena concept cards, duel end cards) are runtime assets.
  - `assets/promotional/`: Storefront banners, itch covers, social media cards, web favicons.
  - `.DS_Store`, `__pycache__`, tests, and development artifacts.
- **No Redundant Asset Duplication**:
  - In macOS `.app` bundles, assets must reside in `Contents/Resources/assets/`, NEVER duplicated simultaneously into `Contents/MacOS/assets/` or multiple subfolders.
  - In Windows onedir builds, assets reside in `SamuraiEdge/assets/`, NEVER duplicated into `_internal/assets/`.
- **Target Size Ceiling**:
  A clean production release package must remain under ~250 MB compressed. If a release `.zip` approaches ~400 MB+, immediately inspect the archive for leaked drafts, raw video takes, or asset duplications.
- **Spec & CI Synchronization**:
  Always ensure `samurai_edge.spec`, `buildozer.spec`, and CI workflows (`.github/workflows/release.yml`, `.github/workflows/release-demo.yml`, `deploy/push_to_itch.sh`) use the `get_runtime_assets` filter and omit redundant copy steps.

## 12. Mandatory Expansion Cycle Pipeline (Strict Execution Order)
Whenever executing a new Roadmap Expansion Cycle (adding new fighters and arenas), ALWAYS strictly follow this 6-step sequential order without skipping or inverting steps:
1. **Full-Body Portrait Concepts & 16:9 Arena Concepts First**:
   - Generate the vertical **Portrait Full-Body Concept Art** (`assets/concepts/<fighter>_full_concept.jpg`) for each new fighter to establish proportions, attire, weapons, and silhouette.
   - Generate the **16:9 Widescreen Arena Concept Art** (`assets/concepts/<arena>_concept.jpg`) for each new stage.
2. **Square Bust Crop & Oval/Circular Framed Portrait**:
   - Derive/generate the **Square Bust Portrait (`256x256`)** (`assets/portraits/<fighter>_bust.png`) and the **Oval/Circular Framed Portrait** (`assets/portraits/<fighter>_circle.png`) directly from the approved character concept.
3. **3D Sculpted Models (Fighters & Arenas)**:
   - Build the 3D faceted low-poly character models (`src/entities/head_<fighter>.py` & `src/entities/body_<fighter>.py`) and 3D arena props/layouts (`src/world/decor.py` & `src/world/arenas.py`) strictly matching the visual concepts.
4. **Suno / Gemini BGM Music Prompts (`GEMINI.md` & `docs/GEMINI_MUSIC_PROMPTS.md`)**:
   - Document the specialized Suno / Gemini music generation prompts (BPM, musical scale/mode, traditional & orchestral instrumentation, loop structure) in both `GEMINI.md` and `docs/GEMINI_MUSIC_PROMPTS.md`.
5. **Gameplay, Fatalities, Hazards & Revamps Implementation**:
   - Implement the fighter combat classes, paired 3D fatalities, stage hazards, classic arena visual revamps, Model/Arena/Studio Inspector synchronization, Game Help entries, Arcade Mode progression, and automated tests.

### Active Suno / Gemini BGM Prompts Reference (Cycle 5):
- **Floresta dos Pinheiros (`bgm_pine_forest.mp3` — Daiki)**:
  - *Prompt (Suno / Gemini)*: `Traditional Japanese Bakumatsu fighting game stage soundtrack, 122 BPM, D Dorian / Yo-scale, virtuous shakuhachi bamboo flute lead echoing through a misty mountain red pine forest at dawn, driving taiko o-daiko and shime-daiko percussion, rhythmic wooden clappers (hyoshigi) and resonant oak bo-staff strikes, plucked shamisen and biwa accents, cinematic orchestral strings, seamless loopable combat track, no vocals.`
- **Taiga de Ezo (`bgm_ezo_taiga.mp3` — Aoi)**:
  - *Prompt (Suno / Gemini)*: `Northern Hokkaido Ezo wilderness fighting game soundtrack, 128 BPM, A Minor pentatonic with traditional Ainu folk motifs, resonant mukkuri (Ainu bamboo jaw harp) and tonkori (five-stringed zither) rhythms, deep tribal frame drums and taiko, icy wind atmosphere, intense staccato pizzicato strings and brass swells evoking a snowy taiga hunt, seamless loopable combat track, no vocals.`

### Active Suno / Gemini BGM Prompts Reference (Cycle 6):
- **Dohyo Sagrado (`bgm_sacred_dohyo.mp3` — Raiden)**:
  - *Prompt (Suno / Gemini)*: `Ancient Japanese Shinto shrine sumo tournament battle theme, 126 BPM, massive ceremonial O-daiko taiko thunder strikes, hyper-resonant hyoshigi wooden clappers and rhythmic referee kakegoe shouts, booming brass and majestic low strings, solemn Gagaku ryuteki flute and hichiriki harmonies evoking divine sumo ritual and unstoppable physical mass, driving cinematic combat progression, loopable, no vocals.`
- **Armazém de Dejima com Doca Chuvosa (`bgm_dejima_dock.mp3` — Hendrika)**:
  - *Prompt (Suno / Gemini)*: `19th-century Bakumatsu Nagasaki Dejima harbor soundtrack, 124 BPM, stormy rainy atmosphere with driving rain and thunder swells, clash of Dutch Baroque harpsichord and virtuoso classical violin with Japanese koto and shakuhachi, eccentric ticking clockwork rhythms, sinister low cello and bassoon arpeggios evoking clandestine alchemy experiments and slippery nighttime harbor intrigue, loopable combat battle theme, no vocals.`

