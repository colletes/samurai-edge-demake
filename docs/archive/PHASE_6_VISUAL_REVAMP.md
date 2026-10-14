# 🎨 PHASE 6: VISUAL REVAMP — From "Basic App" to Oriental Samurai Spectacle

> **Objective:** Transform Samurai Edge from a mechanically-solid game with generic presentation into a **visually cohesive, ornate, HD-2D inspired oriental masterpiece** that matches the quality of character portraits.  
> **Inspired By:** Octopath Traveler (HD-2D), Rurouni Kenshin, Samurai Champloo, Basilisk, Traditional Japanese art, Retro pixel art (Samurai Shodown).  
> **Tone:** **Rich & Ornate** — detailed, layered elegance, visual density, cultural authenticity.  
> **Technical Constraint:** Maintain current performance on **both desktop AND mobile equally**.  
> **Build Sequence:** UI/Menus first → then arena visuals.

---

## 📊 Phase 6 Structure: 6 Iterative Sprints

### **Sprint 0: Design System & Asset Foundation** ✨
*Establish the visual language that ALL future work follows.*

#### 0.1 Color Palette System (Per-Arena)
- [ ] Define **2 base color schemes** for current arenas (Bamboo Forest & Kyoto Bakumatsu)
  - **Bamboo Forest (Cool/Muted):** Forest greens, stone grays, water blues, bamboo tans, cream accents
  - **Kyoto Bakumatsu (Warm/Dramatic):** Deep reds, golds, burnt oranges, charcoal blacks, white highlights
- [ ] Create **template for 12 new arenas** (varied warm/cool mix):
  - 4 warm-palette arenas (temples, farmland, markets)
  - 4 cool-palette arenas (snow, water, night)
  - 4 mixed-palette arenas (sunset, dusk, transition zones)
- [ ] **Deliverable:** `assets/design/color_palettes.json` with hex values, swatches, and usage guidelines

#### 0.2 Font Selection & Implementation
- [ ] Replace system fonts with 2 elegant Japanese-inspired typefaces:
  - **Heading Font:** Serif, traditional (consider: Noto Serif JP, or brush-style like "Shojoru")
  - **Body Font:** Clean, readable, slightly stylized (Noto Sans JP, Zen Antique Soft)
- [ ] Create font rendering module: `src/ui/font_manager.py`
  - Caching for rendered text (avoid per-frame re-renders)
  - Support for layering text (outline + shadow for depth)
  - Multi-line text alignment (center, left, right)
- [ ] **Deliverable:** Elegant fonts integrated into all UI elements; custom text outlines/shadows

#### 0.3 Frame & Panel Design System
- [ ] Design **5 modular panel styles** (reusable components):
  1. **Ornate Frame** (decorative corners, gold/bronze accents) — for titles, character select
  2. **Paper Scroll** (top/bottom curl, aged parchment texture) — for menus, stats
  3. **Lacquer Panel** (glossy, layered, shadow depth) — for HUD, cooldowns
  4. **Ink Wash** (semi-transparent, watercolor edges) — for modals, overlays
  5. **Shrine Gate** (architectural, grid pattern) — for battle arenas, boss intros
- [ ] Generate frame SVGs or pixel-art borders
- [ ] **Deliverable:** `assets/ui/frames/` folder with 5 panel types; `src/ui/panel_renderer.py` to apply them

#### 0.4 Animation & Transition Library
- [ ] Create reusable animation curves:
  - Fade-in (subtle, 0.3s)
  - Slide-from-left / Slide-from-right (smooth easing, 0.4s)
  - Bounce-scale (character select highlight, playful, 0.2s)
  - Pulse (health low warning, rhythmic)
  - Zoom-blur (dramatic reveal, hero shot, 0.5s)
- [ ] **Deliverable:** `src/ui/animations.py` with tweening library; pre-built sequences for common transitions

---

### **Sprint 1: Title Screen & Main Menu Overhaul** 🎭
*First impression — make it unforgettable.*

#### 1.1 Title Screen Redesign
- [ ] **Current state:** Basic video playback + "Press Start"
- [ ] **New vision:**
  - Ornate frame around video with animated borders (brushstroke effect)
  - Animated Japanese calligraphy for "Samurai Edge" title (ink bloom-in effect)
  - Layered background (subtle pattern, silk texture overlay)
  - "Press Start" text with pulsing glow, elegant font
  - Soft ambient music crossfade from opening video
- [ ] **Deliverable:** Redesigned `main.py` title screen; new assets in `assets/ui/title/`

#### 1.2 Main Menu Redesign
- [ ] **Layout:** Centered vertical menu with ornate frame
- [ ] **Options:** Play, Settings, Manual, Quit
  - Each option: hover highlight (glow + subtle scale-up)
  - Selected option: animated underline or bracket animation
- [ ] **Visual Elements:**
  - Watercolor ink-wash background (semi-transparent, shifts slowly)
  - Decorative corner ornaments (top-left, top-right, bottom-left, bottom-right)
  - Soft shadow beneath text for depth
  - Gentle background parallax or subtle animation
- [ ] **Deliverable:** `src/ui/main_menu.py` (new module); frame assets; menu sfx audio cues

#### 1.3 Settings Menu Polish
- [ ] Add visual toggles (not just on/off text):
  - Volume sliders with icon feedback (speaker graphics)
  - Gamepad rumble visualization (little vibration indicator)
  - Language select with flag icons or Japanese/English labels
- [ ] Background blur or darkened overlay (modal aesthetic)
- [ ] **Deliverable:** Enhanced `src/ui/settings_menu.py` with visual components

---

### **Sprint 2: Character Select Screen Transformation** 👥
*Celebrate each warrior with visual flair.*

#### 2.1 Character Portrait Display
- [ ] **Current:** Grid of character names
- [ ] **New vision:**
  - Large character portrait (HD, centered, ornate frame)
  - Animated entrance: portrait slides in from side with slight scale-up
  - Character name below portrait in elegant font with decorative underline
  - Brief flavor text or stat display (health, speed, range archetype) below
  - **Selection highlight:** Ornate frame animates around selected character (gold glow, pulsing)
- [ ] **Deliverable:** New `src/ui/character_select.py` module; frame assets

#### 2.2 Character Stats Presentation
- [ ] Display 3-4 key stats per character in a compact, visual way:
  - **Speed** (icon + bar)
  - **Range** (icon + bar)
  - **Defense** (icon + bar)
  - **Gimmick/Archetype** label (e.g., "Aerial Dancer", "Stealth Assassin", "Cannon Master")
- [ ] Use icon set (small SVGs, consistent with PlayStation button icons)
- [ ] **Deliverable:** Stats layout in character select; SVG icon set for stat types

#### 2.3 Arena Selection Screen (Pre-Battle)
- [ ] Show arena name, thumbnail preview, theme description
- [ ] Animated background showing the arena (blurred, atmospheric)
- [ ] Decorative frame with cultural flavor (e.g., shrine gate for Japanese arenas)
- [ ] **Deliverable:** New `src/ui/arena_select.py` module; arena thumbnail generator

---

### **Sprint 3: In-Game HUD Redesign** 💚
*Clarity + elegance during intense combat.*

#### 3.1 Health Display
- [ ] **Current:** Simple numeric or basic bar
- [ ] **New vision:**
  - Ornate frame (top-left for P1, top-right for P2)
  - Character portrait thumbnail + name
  - Elegant health bar (not flat rectangle — curved, layered, with border gradient)
  - Low health animation: bar flashes red/orange, pulsing glow
- [ ] **Deliverable:** `src/ui/hud_system.py` (refactored); frame assets

#### 3.2 Cooldown Indicators
- [ ] **Current:** Simple numbers or basic cooldown text
- [ ] **New vision:**
  - Circular progress indicator (weapon icon in center, arc around it fills on cooldown)
  - Color coding: green (ready) → yellow (cooldown active) → red (unavailable)
  - Smooth animation as cooldown ticks
  - Icon per ability (sword, bomb, dash, etc. — reuse from design system)
- [ ] Position: Right side of screen, vertically stacked per character
- [ ] **Deliverable:** Circular cooldown UI component; ability icon set

#### 3.3 Attack/Status Indicator
- [ ] Add visual feedback when attacking, parrying, hit:
  - Attack indicator: subtle glow around character hitbox
  - Parry indicator: shield flash or energy ring
  - Hit indicator: red flash + screen shake (already done)
- [ ] **Deliverable:** Enhanced VFX in `src/effects/`

#### 3.4 Combo/Streak Counter (Optional but Polish)
- [ ] If applicable: display current combo count in ornate box
- [ ] Animation: counter increments with bounce-scale effect
- [ ] **Deliverable:** New HUD component (if desired)

---

### **Sprint 4: Modals & Overlay Redesign** 🖼️
*Pause menu, manual, dialogs — every interaction feels intentional.*

#### 4.1 Pause Menu
- [ ] **Current:** Simple text overlay
- [ ] **New vision:**
  - Ink-wash semi-transparent background (darkens arena slightly)
  - Ornate frame (lacquer panel style) in center of screen
  - Title: "Pause" in large elegant font
  - Options: Resume, Settings, Manual, Quit to Menu
  - Each option: hover highlight (underline animation or glow)
  - Background arena still faintly visible (not completely black)
- [ ] **Deliverable:** `src/ui/pause_menu.py` (new module)

#### 4.2 Manual/Help Modal
- [ ] **Current:** Text overlay
- [ ] **New vision:**
  - Paper scroll frame (aged parchment look)
  - Tabbed layout (Controls, Tactics, About)
  - Scrollable content if needed
  - Decorative dividers between sections
  - Close button (X) in ornate frame top-right
- [ ] **Deliverable:** `src/ui/manual_modal.py` (new or enhanced)

#### 4.3 Settings Modal
- [ ] Scroll frame background
- [ ] Visual sliders (not just numbers)
- [ ] Toggle switches (on/off icons, not just text)
- [ ] Color-coded sections (audio, input, visual, language)
- [ ] **Deliverable:** Enhanced settings visual hierarchy

#### 4.4 Victory & Defeat Screens
- [ ] **Victory Screen:**
  - Large "VICTORY!" text in dramatic font (animated entrance, bloom/glow effect)
  - Character portrait (winner) in ornate frame, scaled large
  - Stats display: Time elapsed, hits landed, special moves used
  - "Press to Continue" text at bottom
  - Background: arena lighting shift (celebratory, gold-tinted)
  - Optional confetti/particle effect (subtle, not overwhelming)
- [ ] **Defeat Screen:**
  - Large "DEFEAT" text in somber font
  - Opponent portrait in ornate frame
  - Stats: Damage taken, mistakes made
  - Motivational quote or skill tip
  - "Press to Retry / Return to Menu" options
- [ ] **Deliverable:** `src/ui/victory_modal.py` and `src/ui/defeat_modal.py`

---

### **Sprint 5: Transition Effects & Polish** ✨
*Screen-to-screen continuity.*

#### 5.1 Fade Transitions
- [ ] Fade-to-black between major screens (0.3s smooth)
- [ ] Fade-in from black when entering new screen
- [ ] Implement in: Main Menu → Character Select → Arena Select → Battle → Victory → Main Menu
- [ ] **Deliverable:** `src/ui/transitions.py` (central transition manager)

#### 5.2 Scene-Specific Transitions
- [ ] **Menu to Battle:** Slide-out from right, dramatic zoom effect
- [ ] **Battle to Victory:** Screen freezes (hitstop), victory modal slides in from top
- [ ] **Arena environment fades in:** New arena arenas deserve entrance animation
- [ ] **Deliverable:** Transition choreography in `src/ui/transitions.py`

#### 5.3 HUD Entrance Animation
- [ ] Health/cooldown UI slides in from edges when battle starts
- [ ] Smooth, non-obstructive (doesn't block view of battle)
- [ ] **Deliverable:** HUD initialization in battle state

---

### **Sprint 6: Arena Visual Foundation (2 Current Arenas)** 🏯
*Template for future 12 arenas.*

#### 6.1 Bamboo Forest (Cool Palette Iteration)
**Color Scheme:** Forest green, stone gray, water blue, bamboo tan, cream accents

- [ ] **Environment detail:**
  - Add more bamboo variety (different heights, layering)
  - Moss-covered stones, grass tufts
  - Lanterns (decorative, non-interactive) in background
  - Stone path hints on ground
  - Background trees/forest depth layers

- [ ] **Lighting & Atmosphere:**
  - Soft green-tinted ambient light (forest glow)
  - Dappled shadows from bamboo (subtle parallax, shifts slowly)
  - Mist particles near water (very subtle, low opacity)
  - Time-of-day: Morning/midday feel

- [ ] **Color Grading:**
  - Slightly desaturated but rich greens
  - Cool shadows (blue-gray tones)
  - Highlight water in blues and teals

- [ ] **Technical Implementation:**
  - Add layered background sprite or voxel objects
  - Implement fog particles (low draw cost)
  - Lighting tint applied to arena (shader or color overlay)
  - **Deliverable:** Updated `src/world/bamboo_arena.py`; new voxel assets

#### 6.2 Kyoto Bakumatsu (Warm Palette Iteration)
**Color Scheme:** Deep reds, golds, burnt orange, charcoal black, white highlights

- [ ] **Environment detail:**
  - Refined carriage design (more detail, gilded accents)
  - Debris piles (ashes, wood fragments) with better shading
  - Flames on rooftop (more stylized, flickering effect)
  - Distant pagoda or temple silhouette (background depth)
  - Crumbling walls, battle scars on ground
  - Cherry blossom petals (slow drift, accent color)

- [ ] **Lighting & Atmosphere:**
  - Warm amber/gold ambient light (setting sun or fire glow)
  - Dynamic fire light flicker (subtle, non-distracting)
  - Long shadows (dramatic, eastern light angle)
  - Ash particles drifting (very sparse, silhouette backlit)

- [ ] **Color Grading:**
  - Deep reds and oranges in shadows
  - Bright golds and whites in highlights
  - Slight chromatic aberration or film grain (period feel)

- [ ] **Technical Implementation:**
  - Enhanced voxel models for destruction/detail
  - Animated fire effect (particle or sprite-based, already exists, refine)
  - Layered backgrounds with parallax
  - Ash particle system (low cost, high impact)
  - **Deliverable:** Updated `src/world/kyoto_arena.py`; new voxel + particle assets

#### 6.3 Arena UI Frame
- [ ] Add ornate "Shrine Gate" style frame around arena edges (subtle, not intrusive)
  - Only visible at extreme edges (doesn't interfere with gameplay)
  - Matches arena theme
- [ ] **Deliverable:** Frame overlay assets; arena border rendering

---

### **Sprint 7: Visual Consistency Pass & Documentation** 📖
*Ensure everything coheres; set template for Phase 7 (new 12 arenas).*

#### 7.1 Audit & Refinement
- [ ] Gameplay test pass: Do visuals distract or enhance?
- [ ] Performance test: Maintain 60 FPS on mobile and desktop
- [ ] Consistency check: Do UI, arenas, and character portraits feel like one game?

#### 7.2 Create Arena Template Documentation
- [ ] **Document:** `docs/ARENA_DESIGN_TEMPLATE.md`
  - Color palette workflow
  - Environment detail checklist
  - Lighting setup instructions
  - Performance optimization tips
  - Asset naming conventions
- [ ] **Deliverable:** Clear blueprint for new 12 arenas in Phase 7

#### 7.3 Visual Style Guide
- [ ] **Document:** `docs/VISUAL_STYLE_GUIDE.md`
  - Font usage rules
  - Color palette reference (all palettes)
  - Animation guidelines
  - Frame/modal hierarchy
  - Do's and don'ts
- [ ] **Deliverable:** Reference for future contributors

---

## 🎯 Deliverables Summary

| Sprint | Key Outputs | Files |
|--------|------------|-------|
| **0** | Design system, fonts, frames, animations | `assets/design/`, `assets/ui/frames/`, `src/ui/animations.py`, `src/ui/font_manager.py` |
| **1** | Title & main menu overhaul | `main.py` (updated), `src/ui/main_menu.py`, `assets/ui/title/` |
| **2** | Character & arena select | `src/ui/character_select.py`, `src/ui/arena_select.py`, `assets/ui/portraits/` (enhanced) |
| **3** | HUD redesign (health, cooldowns, feedback) | `src/ui/hud_system.py`, `src/effects/` (VFX enhancements) |
| **4** | Pause, manual, modals, victory/defeat | `src/ui/pause_menu.py`, `src/ui/manual_modal.py`, `src/ui/victory_modal.py`, `src/ui/defeat_modal.py` |
| **5** | Transitions & screen choreography | `src/ui/transitions.py` (new central manager) |
| **6** | Arena visual iteration (Bamboo & Kyoto) | `src/world/bamboo_arena.py`, `src/world/kyoto_arena.py`, `assets/voxel/`, `assets/particles/` |
| **7** | Audit, template, style guide | `docs/ARENA_DESIGN_TEMPLATE.md`, `docs/VISUAL_STYLE_GUIDE.md` |

---

## 🔄 Integration Notes

- **No breaking changes** to existing combat/mechanic systems
- All visual improvements are **additive** (modular, can toggle for performance if needed)
- After Sprint 6, Phase 6 is **complete** and Phase 7 (new 12 arenas + Arcade mode + Gashadokuro boss) can begin immediately with clear templates

---

## 📈 Success Criteria

- ✅ Game no longer looks like "basic application" — distinctly oriental samurai aesthetic
- ✅ Rich, ornate visual language (layered, detailed, elegant)
- ✅ All UI elements unified with custom fonts, frames, animations
- ✅ 2 current arenas visually transformed; template ready for 12 new ones
- ✅ Performance maintained: 60 FPS desktop, 30+ FPS mobile
- ✅ HD-2D visual direction established (matches character portrait quality)

