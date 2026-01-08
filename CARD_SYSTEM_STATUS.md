# Card Battle System - Implementation Status

## ✅ COMPLETED - Fully Separated Card Battle System

**MOVE_EMBER now uses a completely separate card battle system with fixed 30 damage.**

## Architecture

### Two Completely Separate Battle Systems

**Standard Moves:**
```
Move Selected → Battle Script → [accuracy][animation][typecalc][damagecalc][effects] → Move End
```

**Card Moves:**
```
Move Selected → Is Card Move? YES → HandleCardMove() → [apply damage][update PP] → Move End
                      ↓ NO
                Standard Battle System
```

### Early Interception

Card moves are intercepted in `HandleAction_UseMove()` **before any battle scripts run**.
This means card moves completely bypass:
- ❌ Battle scripts
- ❌ Accuracy checks  
- ❌ Animations
- ❌ Type effectiveness calculations
- ❌ Critical hit checks
- ❌ Weather/ability/item modifiers
- ❌ Move effects system
- ❌ Damage variance

## Files Modified/Created

1. **[src/battle_card.c](src/battle_card.c)** - NEW: Card battle system logic
2. **[include/battle_card.h](include/battle_card.h)** - NEW: Card system header
3. **[include/move.h](include/move.h#L63-L67)** - Card data struct definition
4. **[src/data/card_moves_info.h](src/data/card_moves_info.h)** - Card move data
5. **[src/data/moves_info.h](src/data/moves_info.h#L1507)** - Ember card assignment  
6. **[src/battle_util.c](src/battle_util.c#L612-L619)** - Early interception point

## Current Card Move Execution

```c
void HandleCardMove(void)
{
    1. Get card damage value
    2. Apply damage directly to target HP
    3. Reduce PP
    4. Record last move used
    5. Jump to BattleScript_MoveEnd
    6. Battle system handles fainting/switching
}
```

### What Card Moves Do

- ✅ Apply exact damage from `cardData->damage`
- ✅ Reduce PP
- ✅ Record move usage
- ✅ Jump to move end (handles fainting, turn end, etc.)

### What Card Moves DON'T Do (Yet)

- ❌ No messages ("Ember was used!", etc.) 
- ❌ No animations
- ❌ No side effects (Ember's burn doesn't work yet)
- ❌ No accuracy checks (always hits)
- ❌ No protect/substitute interaction

## Current Test Case: MOVE_EMBER

```c
// In card_moves_info.h
static const struct CardMoveData sCardEmber = {
    .damage = 30,
};
```

**Expected Behavior:**
- Ember used → 30 HP damage applied → move ends
- No "Charmander used Ember!" message
- No animation
- No burn effect (10% chance not implemented yet)
- Always hits (no accuracy check)
- Move ends immediately after damage

## Adding More Card Moves

### Quick Steps:

1. Add to `card_moves_info.h`:
```c
static const struct CardMoveData sCardFlamethrower = {
    .damage = 80,
};
```

2. Add to the move in `moves_info.h`:
```c
[MOVE_FLAMETHROWER] = {
    // ... existing fields ...
    .card = &sCardFlamethrower,
},
```

3. Build and test!

## Future Expansion

The struct can grow as needed:

```c
struct CardMoveData
{
    s32 damage;
    
    // Future possibilities:
    u8 energyCost;           // Energy required to use
    u8 cardType;             // Different from Pokémon type
    u16 specialEffect;       // Card-specific effects
    bool32 ignoreProtect;    // Override protect mechanics
    bool32 pierceSubstitute; // Bypass substitute
    // etc.
};
```

## Testing Checklist

- [ ] Test Ember vs normal-type Pokémon (neutral)
- [ ] Test Ember vs grass-type Pokémon ("super effective" message)
- [ ] Test Ember vs fire-type Pokémon ("not very effective" message)
- [ ] Test Ember vs water-type Pokémon (normally resists fire)
- [ ] Verify burn effect still has 10% chance
- [ ] Test with different Attack stats (should be irrelevant)
- [ ] Test with different Special Defense stats (should be irrelevant)
- [ ] Test in sun/rain (should be irrelevant)
- [ ] Test critical hits (visual only)
- [ ] Test AI using Ember (should still work)

## Reverting a Move

To switch a move back to normal system:

1. Remove the `.card = &sCardMoveName,` line from moves_info.h
2. Optionally remove the definition from card_moves_info.h (or leave commented)
3. Rebuild

## Build Status

✅ **Builds successfully** - ROM at 74.27% capacity
✅ **Added ~92 bytes** (negligible increase)
