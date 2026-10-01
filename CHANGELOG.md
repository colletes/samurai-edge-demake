# Changelog

All notable changes to Samurai Edge Demake are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

