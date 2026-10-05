# Changelog

All notable changes to Samurai Edge Demake are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

