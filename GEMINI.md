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
