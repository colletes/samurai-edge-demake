# Changelog

All notable changes to Samurai Edge Demake are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.8.0] - 2026-10-14

### Added
- **Cycle 2 Expansion (Roster 16 Playable Fighters)**:
  - **Benkei** (Sōhei Warrior Monk / Walking Tank): speed 4.0, no parry, colossal 3.0-tile naginata thrust, screen-wide naginata throw with anti-pit safety clamp, unarmed tackle charge with guaranteed 1.2s stun, and ground weapon recovery.
  - **O-Rin** (Acoustic Courtesan Minstrel / Pure Zoner): speed 4.9, open piercing amber eyes, red kumadori eyeliner, higanbana neck tattoo, silver bell earrings, tsugaru shamisen, 6.0-tile Kamaitachi vacuum blade projectile, and 360° Acoustic Resonance shockwave deflecting light projectiles and pushing rivals.
- **New Arenas**:
  - **Ponte Gojo** (`gojo_bridge`): legendary weathered timber bridge over turbulent Kamo River void, stone lanterns, trophy spears/katanas, and river mist atmosphere (`bgm_gojo_bridge.mp3`).
  - **Beco Yoshiwara** (`yoshiwara_alley`): rain-slicked cobblestone alleyway in Kyoto's pleasure quarter, glowing red chōchin lanterns, dark machiya facades, and destrutible folding screens (`bgm_yoshiwara_alley.mp3`).
- **Arena Visual Revamps (Cycle 2)**:
  - **Forest Camp** (`forest_camp`): dynamic campfire ember sparks, drifting autumn leaves, ambient moonlight, and forest fireflies.
  - **Baroque Court** (`baroque_court`): marble fountain steam/mist spray, drifting white and crimson rose petals, and refined baroque sunbeam lighting.
- **Cinematic Presentation Overhaul (Samurai Cinema & Finishers)**:
  - **Dynamic Camera & Anamorphic CinemaScope (2.39:1)**: Smooth zoom to 1.65x centered on the midpoint between fighters, slow atmospheric azimuth rotation (`0.18 rad/s`), and CinemaScope black bars with subtle gold filigree. Smooth pull-back handoff upon corpse collapse to the winner's victory sequence.
  - **Dynamic Sumi-E Calligraphy (*Slash & Stamp*)**: High-speed sweeping diagonal ink brush stroke, Kanji drop-in with impact deceleration (1.30x -> 1.0x), and crimson Inkan seal stamp with exploding red ink dust particles.
  - **Procedural Heartbeat Tension**: Procedural low-frequency double heartbeat (*lub-dub*, 52Hz/44Hz dual pulse with exponential decay) during the hitstop freeze tension, preserving victory BGM upon death resolution.
  - **Enhanced Multi-Stage Finishers & Input Lockout**: Multi-stage fatalities for Benkei (*Naginata Hoist & Slam*), O-Rin (*Sonic Slicer* with 0.7s sepulchral silence), Joe & Yamato (*Windmill Shuriken Decapitation*), and Julie (*Rapier Flurry & Point-Blank Flintlock*). All input cancellation is strictly locked during cinematic execution.
- **Cycle 2 Feedback Fixes & Polish**:
  - Safe ground recovery for thrown weapons: fixed `recover_naginata` collision crash when non-Benkei characters walk over the weapon.
  - Yoshiwara destructible screens: paper folding screens (`ScreenPanel`) shatter into wood splinter particles upon hit.
  - Yoshiwara alley night life aesthetics: removed burning flames on buildings, enhanced nocturnal neon chōchin reflections.
  - Concept art portraits: integrated concept previews for Shaolin Temple and Higanbana Garden into stage carousel.
  - Shaolin Temple Bell: interactive bell hazard triggers expanding circular sonic shockwave (up to half arena) with stun.
  - Shaolin ambiance: procedural voxel crickets and wildlife roaming the Shaolin arena.

## [1.7.0] - 2026-10-10

### Added
- **Cycle 1 Expansion (Roster 14 Playable Fighters)**:
  - **Ren** (Shaolin Martial Monk): speed 5.3, martial arts punch combos, 360° Kiai shout repelling projectiles and stunning enemies.
  - **Chiyo** (Twin Kodachi Kunoichi): speed 5.1, double scissor slash (2.35 tiles), and Mai spinning vortex dance with projectile deflection and riposte.
- **New Arenas (Cycle 1)**:
  - **Pátio dos Sinos Shaolin** (`shaolin_temple`) and **Jardim dos Lírios Carmim** (`higanbana_garden`).
- **Arena Visual Revamps (Cycle 1)**:
  - **Nagashino Field** (`nagashino_field`) & **Shadow Cave** (`shadow_cave`).
- **Cycle 1 Fatalities**: `HYAKURETSU_BODY_EXPLOSION`, `WALL_SMASH_FATAL`, `TRIPLE_SCISSOR_CLEAVE`, `MAI_X_CLEAVE`.

## [1.6.0] - 2026-10-06

### Added
- Oni Gashadokuro: menacing kabuto-skull head (gold crest, horns, glowing eyes), bones and ribs rebuilt from small voxels, much shorter cooldowns between moves, and stage hazards that grow with each phase (falling fireballs, corner-to-corner lava streams, bone-spike traps)
- Endurance and ninja challenge HUD: round dots now track the whole challenge (4 and 8) with an "opponent n/m" counter
- Julie: musketeer roll as the third action (large, clears pits, deflects projectiles)

### Changed
- Challenge fights restore the player's two round lives against each new opponent
- Arcade duel order still follows the balance tiers, but opponents close in tier now shuffle each run
- Julie's secondary action is contextual: flintlock shot when ready, cape flip while the pistol reloads
- Damage and kill messages no longer float above fighters; status, parry, deflection and clash messages remain

## [1.5.0] - 2026-10-05

### Added
- **Arcade mode**: 11-fight journey (7 duels, mirror match, endurance 1x2, ninja challenge, final boss) with infinite counted Continues, dynamic AI difficulty, scoring, high scores and resumable runs
- **Oni Gashadokuro**: 5-phase voxel skeleton boss with telegraphed attacks, its own arena and per-phase checkpoints
- Per-character intro and victory animations, with an end-of-round sequence (knockout replay, victory pose)
- Hit knockback, knockout replay camera, HUD damage bars and voxel corpses
- Default language detected from the system (`SAMURAI_EDGE_LANG` overrides it)
- Demo edition (itch.io `-demo` channels): Kenshi and Tomoe only, Kenshi's arena, 1P or 2P, no Arcade

### Removed
- Cel shading option and models

## [1.4.0] - 2026-10-04

### Added
- **Phase 6 arenas**: 12 themed arenas with generator, hazards, structures, selection screens, lighting/atmosphere, shared wind, terrain particles and volumetric fog
- **Phase 6.5 visual refinement**: voxel textures, cloth physics, per-fighter models for all 12 fighters, cel-shading for Kenshi and Murasaki, material textures (latex, silk, velvet, leather, metal)
- Effects quality (high/low) and character style options, persisted in `settings.json`
- Opening cinematic video screen before the Sumi-e title screen
- Round intro/result screens (best-of-3) and clash QTE system
- Full PT/EN translation, including character and arena screens
- Round help button icon
- Sprite sheet and arena gallery tools, music prompts, new tests

### Changed
- Procedural SFX rewrite with rendered WAV assets
- Controller-aware button prompts (PlayStation, Xbox, Switch, generic) and translated key/button names
- Fighter balance and AI difficulty updates
- Baked opacity for fog/smoke sprites instead of per-frame alpha

### Fixed
- Kunai pickup crash for projectile owners without `has_kunai`
- Help modal, settings menu and title screen layout crashes/regressions
- Settings and character-select labels overflowing their boxes

## [1.3.6] - 2026-10-01

### Changed - Balance

#### Musashi (Blue Samurai) Phase 2: Aggressive Rebalancing
- **3 HP System (Musashi-only)**: Requires 3 hits to KO instead of 2
  - +50% durability advantage vs all other 2-HP characters
  - Allows surviving initial rushes and trading hits more favorably
  - Maintains 1-damage projectile vulnerability for balanced high-pressure play
  
- **AI Parry Bonus Boost**: Increased from 0.55 to 0.70 (+27% improvement)
  - Better automated projectile defense against ranged pressure
  - Effective vs high-tier zoners (Teppo 73.5%, Tomoe 60.6%)
  - Rewards defensive play while maintaining offensive opportunity
  
- **Extended Sword Reach**: +11% on all combo tiers
  - Combo 1: 1.30 → 1.45 radius
  - Combo 2: 1.45 → 1.62 radius
  - Combo 3: 1.85 → 2.06 radius
  - Improves both offense (better hit confirmation distance) and defense (safer spacing control)

### Result
- **Winrate Improvement**: +26.2% stable gain (23.0% → 49.2% average)
- **Tournament Validation**: 51.1%, 47.4%, 49.2% across three independent tournament runs
- **Rank**: Stable 8th-9th place with healthy roster diversity
- **Roster Health**: Teppo 73.5% (top), Okuni 16.3% (bottom), no extreme outliers

### Design Rationale
Triple buffing approach creates synergistic offensive/defensive loop:
- 3 HP allows Musashi to survive initial pressure and trade hits more favorably
- Better parry AI punishes projectile spam more effectively at range
- Extended reach improves both offensive pressure (earlier hit confirms) and defensive safety (better spacing)
- Design avoids single-point-of-failure that damaged previous iterations (resilience -10.2%, damage boost -6.1%, KI Wave deletions)

---

## [1.3.5] - 2026-10-01

### Changed - Balance

#### Musashi (Blue Samurai) Rebalancing
- **Attack Speed Boost**: Reduced combo windup from 0.42s to 0.35s, hit duration from 0.12s to 0.10s
  - +17% DPS improvement, higher pressure against zoners
  - Faster combo execution enables better offense flow
  
- **Reduced Stun Duration**: Stun events now apply 60% of incoming duration
  - 40% faster recovery (e.g., 0.35s stun → 0.21s actual)
  - Enables faster counter-attack opportunities
  - Critical for defensive mixups and combo threading
  
- **Extended Parry Window**: Increased reflection window from 0.22s to 0.28s
  - +27% reaction time for projectile defense
  - More forgiving against fast-moving projectiles (Teppo bullets, Shuriken)
  - Synergizes with existing parry reflection mechanic

### Result
- **Winrate Improvement**: +1.4% stable gain (21.6% baseline → 23.0% average)
- **Tournament Validation**: 22.7%, 24.2%, 22.0% across three independent tournament runs
- **Design Rationale**: Creates positive feedback loop where faster attacks require tighter parry timing, which in turn allows faster recovery and counter-attack capability

### Testing
- Multi-run tournament validation with 1,584 total battles per run (66 matchups × 24 battles)
- No catastrophic regressions; consistent improvement across all test runs
- All other character winrates remain stable

---

## [1.3.4] - 2026-09-28

### Added - Audio

- Integrated original high-fidelity background music (BGM) for all stages
- Full sound effect (SFX) library upgrade to WAV format (lossless)

### Changed

- Audio processing pipeline refactored for better procedural SFX generation

---

## [1.3.3] - 2026-09-25

### Added - Audio

- Integrated acoustic real-world audio samples (26 samples across SFX and BGM)
- Procedural sound event system with fallback safety

### Fixed

- Audio system aliases and metaclass safety improvements

---

## [1.3.0] - 2026-09-15

### Added

- Character roster complete: 12 playable samurai fighters
- Tournament simulation system for balance testing
- Isometric 3D-to-2D rendering pipeline
- Combat collision detection with projectile reflection mechanics

### Changed

- Full rebalancing phase initiated for competitive viability

