# Phase 4 Balance Options - Quick Implementation Guide

## Quick Test: Implement Each Option (Copy-Paste Ready)

### Test 1: Option A (Musashi Stun Increase to 0.50s)
**File**: `src/entities/samurai.py` (Line 223)
```python
# CURRENT (0.35s stun):
self.stun(0.35)

# OPTION A TEST (0.50s stun):
self.stun(0.50)
```

---

### Test 2: Option B (Kenshi Recovery Bonus Reduction to 0.40s)
**File**: `src/entities/red_samurai.py` (Line 48)
```python
# CURRENT (0.25s bonus):
self.state_timer = 0.25

# OPTION B TEST (0.40s bonus):
self.state_timer = 0.40
```

---

### Test 3: Option C (Add Kenshi Knockback - Requires More Work)
**Note**: Knockback requires collision.py modification to pass target reference.
This is the most complex option - recommend testing A, B, A+B, B+C first.

---

### Test 4: Option A+B (Combined Stun + Reduced Bonus)
Apply BOTH changes:
- `src/entities/samurai.py` line 223: Change 0.35 → 0.50
- `src/entities/red_samurai.py` line 48: Change 0.25 → 0.40

---

### Test 5: Option B+C (Reduced Bonus + Knockback)
Apply Option B only (knockback requires collision.py rework)

---

### Test 6: Option A+C (Stun + Knockback)
Apply Option A only (knockback requires collision.py rework)

---

## Testing Quick Start

### Step 1: Run Current State (Baseline)
```bash
cd "/Users/thiagocarvalho/Documents/Sample Game"
source venv/bin/activate
python3 main.py
```
Play 3-5 matches: Kenshi vs Musashi (AI difficulty: Normal)
**Observation**: How long are Kenshi's combos? Can Musashi break free?

### Step 2: Test Option B (Recommended First)
Edit `src/entities/red_samurai.py` line 48:
- Change: `self.state_timer = 0.25`
- To: `self.state_timer = 0.40`

Run: `python3 main.py`
Play 5 matches, measure combo lengths
**Expected**: Combos should be ~2-3 hits instead of 5+

### Step 3: Revert and Test Option A
Edit `src/entities/samurai.py` line 223:
- Change: `self.stun(0.35)`
- To: `self.stun(0.50)`

(Revert step 2's change to red_samurai.py)
Run: `python3 main.py`
Play 5 matches
**Compare**: Is this better/worse than Option B?

### Step 4: Test Option A+B (Combined)
Apply BOTH changes together
Play 5 matches
**Evaluate**: Is the combination better?

---

## Measurement Template

### Test Match Record
```
Option: [A / B / C / A+B / B+C / A+C]
Match #: 1-5

Match 1:
  - Duration: [time]
  - Kenshi Combo Length: [#hits]  
  - Musashi Counterattacks: [yes/no]
  - Winner: [Kenshi/Musashi/Draw]
  - Feel: [balanced/kenshi-strong/musashi-strong]

[Repeat for matches 2-5]

AVERAGE COMBO LENGTH: ___
MUSASHI COUNTERATTACK %: ___
KENSHI WIN RATE: ___
OVERALL FEEL: ___________
```

---

## When You've Completed Testing

Pick the BEST option based on:
1. **Combo Length**: Averages 2-3 hits (not 5+)
2. **Win Balance**: Close to 50/50 (40-60% range)
3. **Counterplay**: Musashi can realistically respond
4. **Feel**: Matches play well, no "cheap" exploitation

Then run me the results:
```
Best Option: [Option Name]
Metrics:
  - Avg Combo Length: ___
  - Win Rate (Kenshi): ___%
  - Subjective Feel: _____

I'll implement the final version and clean up for deployment.
```

---

## Reverting Changes (If Needed)

If you mess up a test, just revert files:

**Revert one file**:
```bash
git restore src/entities/red_samurai.py
```

**Revert all changes**:
```bash
git restore .
```

---

## Files Modified Per Option

| Option | samurai.py | red_samurai.py | collision.py |
|--------|-----------|----------------|------------|
| A      | ✓ (0.50s) | -              | -          |
| B      | -         | ✓ (0.40s)      | -          |
| C      | -         | ✓ + ✓          | ✓          |
| A+B    | ✓ (0.50s) | ✓ (0.40s)      | -          |
| B+C    | -         | ✓ (0.40s) + ✓  | ✓          |
| A+C    | ✓ (0.50s) | ✓ + ✓          | ✓          |

Legend: ✓ = modified, - = unchanged
