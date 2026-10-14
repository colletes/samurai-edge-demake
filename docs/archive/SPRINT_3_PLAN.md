# Phase 6 Sprint 3: Character Select Screen Enhancement — PLAN

**Date:** 2026-10-01  
**Duration:** Estimated 2-4 hours  
**Prerequisites:** ✅ Sprint 0 (Design System), ✅ Sprint 1 (Components), ✅ Sprint 2 (Integration)

---

## 📋 Overview

Sprint 3 will redesign the Character Select screen to use the new visual language established in Sprints 0-1:
- Apply **FontManager** for elegant typography
- Use **PanelRenderer** for character card frames
- Integrate **Animations** for smooth transitions
- Maintain current functionality while improving aesthetics

---

## 🎨 Visual Goals

### Before (Current)
- Basic portrait display
- Simple text labels
- Minimal visual hierarchy
- Plain selection highlight

### After (Sprint 3)
- **Ornate character cards** with lacquer panel frames
- **Rich typography** using Japanese serif fonts
- **Animated selection** (glow + scale transitions)
- **Visual stat bars** (Speed, Range, Defense)
- **Smooth hover animations** on card transitions
- **Character name** with decorative underline
- **Archetype badge** (e.g., "Aerial Dancer")
- **Background theme** matching arena palette

---

## 📌 Deliverables

### 3.1 Character Card Design ✨
**File:** Create/enhance `src/ui/character_card.py` (NEW module)

**Features:**
- ```python
  class CharacterCard:
      def __init__(self, character_id, width=200, height=300):
          # Portrait rendering with ornate frame
          # Name + stats display
          # Selection state visual feedback
      
      def render(screen, x, y, selected=False, hovered=False):
          # Render card with animations
          # Selected: ornate gold glow + pulsing animation
          # Hovered: subtle scale-up + highlight
  ```

**Components:**
1. **Card Frame:** Lacquer panel style (from `PanelRenderer`)
2. **Portrait:** Existing character portrait assets
3. **Name:** FontManager (elegant serif, 24pt, centered)
4. **Archetype Badge:** Small label (e.g., "Speed Demon", "Aerial Master")
5. **Stat Bars:**
   - **Speed:** Icon + horizontal bar (1-5 filled segments)
   - **Range:** Icon + horizontal bar
   - **Defense:** Icon + horizontal bar
6. **Selection Highlight:** Animated gold glow + pulsing effect

### 3.2 Character Select Screen Redesign ✨
**File:** Modify `src/ui/character_select.py`

**Current State:**
- Line 1-50: Basic grid layout
- Line 51-150: Portrait display
- Line 151-200: Input handling
- Line 201+: Menu rendering

**Changes:**
1. **Import new components:**
   ```python
   from src.ui.font_manager import FontManager, FontSize, FontFamily
   from src.ui.panel_renderer import PanelRenderer, PanelStyle
   from src.ui.animations import Tween, UIAnimator, Easing
   from src.ui.character_card import CharacterCard
   ```

2. **Create character card grid:**
   ```python
   self.character_cards = [
       CharacterCard(char_id) for char_id in CHAR_IDS
   ]
   self.selected_card_index = 0
   self.hover_scale = 1.0
   self.highlight_alpha = 1.0
   ```

3. **Enhanced rendering:**
   - Background: Ink-wash style with subtle parallax
   - Title: "選び手" (Swordmaster Selection) with serif font
   - Grid: Centered 3x4 or 2x6 card layout
   - Selected card: Ornate frame animates (gold glow + scale)
   - Hover card: Subtle lift effect (scale + y offset)

4. **Input handling improvements:**
   - Arrow keys: Smooth card navigation with scale animation
   - Enter: Confirm selection with bounce effect
   - Esc: Back to main menu
   - Mouse: Click card to select + hover animations

### 3.3 Difficulty Selector Enhancement ✨
**File:** Enhance difficulty selector UI

**Current:** Simple text or button toggle  
**New:**
- **Visual selector:** 3 radio buttons in elegant frame
  - **Easy:** "初心" (Beginner)
  - **Normal:** "武士" (Warrior)
  - **Hard:** "達人" (Master)
- **Description text:** Tooltip-style flavor text
  - Easy: "Perfect for learning combos"
  - Normal: "Balanced challenge"
  - Hard: "Only masters survive"
- **Animated selection:** Glow on active option

---

## 🛠️ Implementation Steps

### Step 1: Create CharacterCard Module
```bash
# Create new module
touch src/ui/character_card.py

# Template structure:
# - CharacterCard class
# - render() method with animations
# - update() for animation ticks
# - get_selected_state() for input
```

### Step 2: Update character_select.py
```bash
# Modify existing screen
# Import new components
# Replace grid rendering with CharacterCard objects
# Add animations to selection/hover states
```

### Step 3: Add Stat Visualization
```bash
# Create stat icons (or reuse from existing assets)
# Implement bar rendering (5 segments)
# Integrate with character data
```

### Step 4: Test All Interactions
```bash
# Keyboard navigation (↑↓←→)
# Mouse hover + click
# Gamepad D-Pad + A/B buttons
# Selection confirmation
# Animation smoothness (60 FPS)
```

---

## 📊 Testing Checklist

- [ ] Character cards load without errors
- [ ] All 12 character portraits display correctly
- [ ] Selected card highlights with gold glow
- [ ] Hover animations smooth (no jank)
- [ ] Arrow key navigation works (all 4 directions)
- [ ] Mouse click selects character
- [ ] Gamepad D-Pad works
- [ ] Enter confirms selection
- [ ] Esc goes back to main menu
- [ ] Difficulty selector updates correctly
- [ ] Animation frame rate stable (60 FPS)
- [ ] No font rendering warnings
- [ ] Settings (e.g., AI difficulty) persist

---

## 🎯 Success Criteria

✅ **Visual**
- Character cards have ornate lacquer frames
- Selection highlight animates (gold glow + pulse)
- Hover animations are smooth
- Typography is elegant (serif fonts)
- Stat bars display correctly

✅ **Functional**
- All 12 characters selectable
- Arrow key navigation works
- Mouse click selection works
- Gamepad navigation works
- Difficulty selector functional
- Settings persist

✅ **Performance**
- 60 FPS stable (no frame drops)
- No memory leaks
- Animation smooth across all transitions

✅ **Code Quality**
- Follows Sprint 0-1 patterns
- Reuses PanelRenderer, FontManager, Animations
- Backward compatible with existing game logic
- Well-commented code

---

## 📁 Files to Create/Modify

| File | Type | Description |
|------|------|-------------|
| `src/ui/character_card.py` | NEW | Character card component |
| `src/ui/character_select.py` | MODIFY | Enhanced screen layout |
| `src/ui/character_select.py` | MODIFY | Add stat visualization |
| `test_sprint3_character_select.py` | NEW | Component testing |

---

## 🔄 Flow After Sprint 3

```
MAIN_MENU
    ↓ (PLAY clicked)
CHARACTER_SELECT (NEW DESIGN) ← You are here
    ↓ (Character + Difficulty selected)
ARENA_SELECT
    ↓ (Arena selected)
DUEL_PLAYING
    ↓ (Match complete)
DUEL_RESULT
```

---

## 📚 Reference

### Existing Components (Reuse)
- **FontManager:** `src/ui/font_manager.py` — Text rendering with effects
- **PanelRenderer:** `src/ui/panel_renderer.py` — Ornate frames (Lacquer style)
- **Animations:** `src/ui/animations.py` — Tween + UIAnimator
- **Color Palettes:** `assets/design/color_palettes.json` — Theme colors

### Current Character Select
- Location: `src/ui/character_select.py`
- Characters: 12 warriors (CHAR_KENSHIN, CHAR_MUSASHI, etc.)
- Current selection: Simple grid + text
- Difficulty: Currently selectable (needs UI enhancement)

### Related Files
- Character data: `src/entities/fighters.py`
- Main game loop: `main.py` (calls character_select.py)

---

## 🎬 Next Steps After Sprint 3

1. **Sprint 4:** Arena Select Screen Enhancement
2. **Sprint 5:** In-Game HUD Redesign (health bars, cooldowns, combat UI)
3. **Sprint 6:** Modals & Overlays (pause menu, manual, dialogs)
4. **Sprint 7:** Arena Visual Overhaul (backgrounds, effects)

---

## ⏱️ Estimated Timeline

- **Preparation:** 10 min (review current code, plan structure)
- **CharacterCard module:** 45 min (class + rendering + animations)
- **Character Select screen update:** 45 min (integration + testing)
- **Testing & refinement:** 30 min (all input methods, performance)
- **Documentation:** 15 min
- **Total:** ~2.5 hours

---

## 💡 Key Implementation Notes

1. **Reuse PanelRenderer:** Don't draw frames manually; use `PanelRenderer.render_panel(style=LACQUER)`
2. **Animate transitions:** Use `UIAnimator.scale()` and `UIAnimator.fade()` for smooth effects
3. **Font consistency:** All text via `FontManager` (no hardcoded pygame fonts)
4. **Stat icons:** Can be simple SVG shapes or emoji for MVP
5. **Input handling:** Maintain current key mappings, add mouse/gamepad feedback
6. **Testing:** Create `test_sprint3_character_select.py` to verify all interactions

---

**Status:** READY TO START ✅
