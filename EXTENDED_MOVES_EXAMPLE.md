# Card Move Data Usage Guide

The `CardMoveData` system allows you to add custom battle system data to moves without breaking existing functionality.

## How It Works

1. **Optional pointer**: Each move has a `card` field that's `NULL` by default
2. **Upgrade moves one at a time**: Only define card data for moves you want to customize
3. **Add fields incrementally**: Start with what you need now, expand later

## Example: Adding Card Data to a Move

### Step 1: Define the card data in `src/data/card_moves_info.h`

```c
// Add this after the description strings, before gMovesInfo array:
static const struct CardMoveData sCardPound = {
    .damage = 50,
};
```

### Step 2: Add the pointer to the move definition

```c
[MOVE_POUND] =
{
    .name = COMPOUND_STRING("Pound"),
    .description = COMPOUND_STRING(
        "Pounds the foe with\n"
        "forelegs or tail."),
    .effect = EFFECT_HIT,
    .power = 40,
    .type = TYPE_NORMAL,
    .accuracy = 100,
    .pp = 35,
    .target = MOVE_TARGET_SELECTED,
    .priority = 0,
    .category = DAMAGE_CATEGORY_PHYSICAL,
    .makesContact = TRUE,
    .ignoresKingsRock = B_UPDATED_MOVE_FLAGS == GEN_4,
    .contestEffect = CONTEST_EFFECT_HIGHLY_APPEALING,
    .contestCategory = CONTEST_CATEGORY_TOUGH,
    .contestComboStarterId = COMBO_STARTER_POUND,
    .contestComboMoves = {0},
    .battleAnimScript = gBattleAnimMove_Pound,
    .card = &sCardPound,  // <-- Add this line
},
```

### Step 3: Use the extended data in battle code

```c
// Example in src/battle_util.c or wherever you need it:
u32 GetCardMoveDamage(u16 move)
{
    const struct MoveInfo *moveInfo = &gMovesInfo[move];
    
    // Check if this move uses extended data
    if (moveInfo->card != NULL)
    {
        // Use the custom damage value
        return moveInfo->card->damage;
    }
    
    // Fall back to normal power calculation
    return moveInfo->power;
}
```

## Adding More Fields

Edit `include/move.h` to add fields to `CardMoveData`:

```c
struct CardMoveData
{
    s32 damage;
    u8 customFlag1;
    u8 customFlag2;
    u16 specialEffect;
    // Add whatever you need!
};
```

## Benefits

- **No ROM bloat**: Only moves with extended data use extra space
- **Safe iteration**: Old moves work unchanged
- **Easy to test**: Enable new system per-move for testing
- **Future-proof**: Add fields without touching existing data

## Memory Impact

- Pointer in MoveInfo: 4 bytes × 850 moves = 3.4 KB
- Each ExtendedMoveData struct: Size depends on your fields
- Only allocated for moves you upgrade
