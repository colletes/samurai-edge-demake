# Phase 4: Musashi vs Kenshi Balance Testing Guide

## Objective
Fix the Musashi vs Kenshi imbalance where Kenshi dominates with infinite combo chains.

## Current State Analysis
- **Musashi HP**: 3 (correct, matches Kenshi)
- **Musashi Stun on Hit**: 0.35s (auto-applied when taking damage)
- **Kenshi Recovery**: 
  - Normal: 0.60s
  - On-hit bonus: 0.25s (reduces by 58%)
- **Issue**: 0.35s stun is shorter than 0.25s on-hit recovery, allowing immediate follow-ups

## Balance Test Options

### Option A: Musashi Stun Increase
**Mechanic**: Increase Musashi's stun duration when hit
**Implementation**:
- Modify: `src/entities/samurai.py` line 223
- Change: `self.stun(0.35)` → `self.stun(0.50)` or `self.stun(0.60)`
- Allows Musashi more time to react before next combo hit

**Pros**:
- No change to Kenshi mechanics
- Proportional response to Musashi being hit
- Gives breathing room against any combo-heavy character

**Cons**:
- Makes Musashi too resilient to other characters' combos
- Might break balance against non-Kenshi opponents
- Creates artificial defense bonus for Musashi

### Option B: Kenshi Recovery Reduction  
**Mechanic**: Reduce Kenshi's on-hit recovery bonus
**Implementation**:
- Modify: `src/entities/red_samurai.py` line 48
- Change: `self.state_timer = 0.25` → `self.state_timer = 0.40`
- Increases gap between Kenshi's hits, giving Musashi time to counterattack

**Pros**:
- Directly nerfs the overpowered bonus
- Still rewards Kenshi for landing hits
- Maintains Kenshi's skill expression (timing dependent)
- Minimal cascade effects on other matchups

**Cons**:
- Kenshi might become too weak
- Reduces reward for successful hits

### Option C: Kenshi Knockback  
**Mechanic**: Add knockback to Kenshi's iai attack on hit
**Implementation**:
- Modify: `src/entities/red_samurai.py` after on-hit code
- Add knockback velocity to hit target after successful hit
- Example: `p1.wx += kenshi.facing_x * 0.5; p1.wy += kenshi.facing_y * 0.5`
- Creates space between fighters, breaking combo chains

**Pros**:
- Rewards skillful spacing/positioning
- Creates dynamic, interactive combat
- Prevents combo lockdown without changing raw stats
- Interesting risk/reward mechanic

**Cons**:
- Might feel unfair (momentum-based combat)
- Could break other character interactions
- Harder to balance precisely

## Testing Protocol

### Preparation
```bash
cd /Users/thiagocarvalho/Documents/Sample\ Game
source venv/bin/activate
python3 main.py
```

### Test Procedure Per Option
**For each of the 6 combinations (A, B, C, A+B, B+C, A+C):**

1. **Implement the changes** (modify the code files as specified above)
2. **Run 5 practice matches**: Kenshi vs Musashi (human vs AI or human vs human)
3. **Measure**: Count average number of consecutive hits Kenshi lands before Musashi can react
4. **Record**: Scoring combo length, counterattack frequency, winner tendency
5. **Assess**: Does it feel balanced? Can Musashi defend/counter? Is Kenshi still viable?

### Scoring Criteria
Each match, measure:
- **Combo Length**: Average # consecutive Kenshi hits before Musashi can act
  - Goal: 2-3 hits max (currently: 5+ hits before stun ends)
- **Counterattack Frequency**: % of time Musashi can land a hit after being hit
  - Goal: > 50% of time
- **Win Rate**: Kenshi wins / total matches
  - Goal: 40-60% (balanced)
- **Matchup Feel**: Subjective - is it fun and fair for both players?

### Test Matrix

| Combination | Recovery Change | Musashi Stun | Kenshi Knockback | Notes |
|------------|-----------------|--------------|------------------|-------|
| A          | (0.25s)         | 0.50-0.60s   | None             | Test pure stun buff |
| B          | 0.40s           | 0.35s        | None             | Test reduced bonus |
| C          | (0.25s)         | 0.35s        | Yes (+0.5m)      | Test spacing |
| A+B        | 0.40s           | 0.50-0.60s   | None             | Combined stun + reduced bonus |
| B+C        | 0.40s           | 0.35s        | Yes (+0.5m)      | Combined reduced bonus + knockback |
| A+C        | (0.25s)         | 0.50-0.60s   | Yes (+0.5m)      | Combined stun + knockback |

## Implementation Details

### Option A: Increase Musashi Stun
File: `src/entities/samurai.py`
```python
# Line 223 - Change from:
self.stun(0.35)
# To:
self.stun(0.50)  # or 0.60 for stronger effect
```

### Option B: Reduce Kenshi Recovery Bonus
File: `src/entities/red_samurai.py`
```python
# Lines 46-48 - Change from:
def on_hit_success(self):
    """Entregável 4.1: Reduz recovery do Iai ao acertar para 0.25s (era 0.35s / 0.80s)."""
    if self.state in (STATE_ATTACK, STATE_RECOVERY):
        self.state = STATE_RECOVERY
        self.state_timer = 0.25

# To:
def on_hit_success(self):
    """Rebalanced: Reduced Iai recovery bonus to 0.40s for better counterplay."""
    if self.state in (STATE_ATTACK, STATE_RECOVERY):
        self.state = STATE_RECOVERY
        self.state_timer = 0.40
```

### Option C: Add Kenshi Knockback
File: `src/entities/red_samurai.py` - Modify `on_hit_success()`
```python
def on_hit_success(self):
    """Rebalanced: Iai attack now includes knockback for spacing."""
    if self.state in (STATE_ATTACK, STATE_RECOVERY):
        self.state = STATE_RECOVERY
        self.state_timer = 0.25
        # Add knockback to the target (passed from collision system)
        # This would require coordination with collision.py
        self.has_knockback_pending = True
        self.knockback_distance = 0.5
```

## Regression Testing

After choosing the best option, test against other characters to ensure no regressions:
- Musashi vs others (American, Ninja, Saitou, etc.)
- Kenshi vs others
- 2P matches with different controllers
- Settings menu responsiveness
- Animation smoothness

## Decision Criteria

Choose the option that:
1. Limits Kenshi combos to 2-3 hits (main objective)
2. Keeps both characters playable (40-60% win rate each)
3. Requires skill from both players
4. Feels "fair" - no cheese strategies
5. Has minimal effects on other matchups

## Status
- Phase 4 Code Changes: PENDING (awaiting test results)
- Current Best Option: To be determined after testing
- Implementation: Will apply after validation

## Notes
- All changes are reversible - revert using git or file restore
- Test in fresh venv: `python3 main.py` after changes
- Take screenshots/video of combo chains for reference
- Record subjective feel (smoothness, fairness, fun factor)
