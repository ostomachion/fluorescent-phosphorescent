# Energy Icons Implementation Guide

This guide shows how to display energy requirement icons instead of letters in the move selection screen.

## Step 1: Create the sprite graphics

Create 9 energy icon sprites (16x16 pixels each) in `graphics/battle_interface/`:
- `energy_grass.png`
- `energy_fire.png`
- `energy_water.png`
- `energy_electric.png`
- `energy_psychic.png`
- `energy_fighting.png`
- `energy_darkness.png`
- `energy_metal.png`
- `energy_colorless.png`

## Step 2: Add graphics rules

Add to `graphics_file_rules.mk`:
```make
$(BATTLEINTERFACEGFXDIR)/energy_icons.4bpp: $(BATTLEINTERFACEGFXDIR)/energy_grass.png \
                                             $(BATTLEINTERFACEGFXDIR)/energy_fire.png \
                                             $(BATTLEINTERFACEGFXDIR)/energy_water.png \
                                             $(BATTLEINTERFACEGFXDIR)/energy_electric.png \
                                             $(BATTLEINTERFACEGFXDIR)/energy_psychic.png \
                                             $(BATTLEINTERFACEGFXDIR)/energy_fighting.png \
                                             $(BATTLEINTERFACEGFXDIR)/energy_darkness.png \
                                             $(BATTLEINTERFACEGFXDIR)/energy_metal.png \
                                             $(BATTLEINTERFACEGFXDIR)/energy_colorless.png
	@echo Converting energy icons...
	$(GFX) $^ $@

$(BATTLEINTERFACEGFXDIR)/energy_icons.gbapal: $(BATTLEINTERFACEGFXDIR)/energy_grass.png
	$(GFX) $< $@
```

## Step 3: Add sprite definitions

Add to `src/battle_controller_player.c` (or new `src/energy_icons.c`):

```c
#include "data.h"

// Tag for energy icon sprites
#define TAG_ENERGY_ICONS 0xD750

// Energy icon indices matching the sprite sheet order
enum EnergyIconType {
    ENERGY_ICON_GRASS = 0,
    ENERGY_ICON_FIRE = 1,
    ENERGY_ICON_WATER = 2,
    ENERGY_ICON_ELECTRIC = 3,
    ENERGY_ICON_PSYCHIC = 4,
    ENERGY_ICON_FIGHTING = 5,
    ENERGY_ICON_DARKNESS = 6,
    ENERGY_ICON_METAL = 7,
    ENERGY_ICON_COLORLESS = 8,
};

#define MAX_ENERGY_ICONS 8

static u8 sEnergyIconSpriteIds[MAX_ENERGY_ICONS];

// Graphics declarations
static const u32 sEnergyIcons_Gfx[] = INCBIN_U32("graphics/battle_interface/energy_icons.4bpp.lz");
static const u16 sEnergyIcons_Pal[] = INCBIN_U16("graphics/battle_interface/energy_icons.gbapal");

static const struct OamData sOamData_EnergyIcons =
{
    .y = 0,
    .affineMode = ST_OAM_AFFINE_OFF,
    .objMode = ST_OAM_OBJ_NORMAL,
    .mosaic = FALSE,
    .bpp = ST_OAM_4BPP,
    .shape = SPRITE_SHAPE(16x16),
    .x = 0,
    .matrixNum = 0,
    .size = SPRITE_SIZE(16x16),
    .tileNum = 0,
    .priority = 1,
    .paletteNum = 0,
    .affineParam = 0,
};

// Animation commands for each energy type
static const union AnimCmd sSpriteAnim_EnergyIcon_Grass[] = {
    ANIMCMD_FRAME(0, 0),
    ANIMCMD_END
};

static const union AnimCmd sSpriteAnim_EnergyIcon_Fire[] = {
    ANIMCMD_FRAME(4, 0),  // 16x16 sprite = 4 tiles
    ANIMCMD_END
};

static const union AnimCmd sSpriteAnim_EnergyIcon_Water[] = {
    ANIMCMD_FRAME(8, 0),
    ANIMCMD_END
};

static const union AnimCmd sSpriteAnim_EnergyIcon_Electric[] = {
    ANIMCMD_FRAME(12, 0),
    ANIMCMD_END
};

static const union AnimCmd sSpriteAnim_EnergyIcon_Psychic[] = {
    ANIMCMD_FRAME(16, 0),
    ANIMCMD_END
};

static const union AnimCmd sSpriteAnim_EnergyIcon_Fighting[] = {
    ANIMCMD_FRAME(20, 0),
    ANIMCMD_END
};

static const union AnimCmd sSpriteAnim_EnergyIcon_Darkness[] = {
    ANIMCMD_FRAME(24, 0),
    ANIMCMD_END
};

static const union AnimCmd sSpriteAnim_EnergyIcon_Metal[] = {
    ANIMCMD_FRAME(28, 0),
    ANIMCMD_END
};

static const union AnimCmd sSpriteAnim_EnergyIcon_Colorless[] = {
    ANIMCMD_FRAME(32, 0),
    ANIMCMD_END
};

static const union AnimCmd *const sSpriteAnimTable_EnergyIcons[] =
{
    sSpriteAnim_EnergyIcon_Grass,
    sSpriteAnim_EnergyIcon_Fire,
    sSpriteAnim_EnergyIcon_Water,
    sSpriteAnim_EnergyIcon_Electric,
    sSpriteAnim_EnergyIcon_Psychic,
    sSpriteAnim_EnergyIcon_Fighting,
    sSpriteAnim_EnergyIcon_Darkness,
    sSpriteAnim_EnergyIcon_Metal,
    sSpriteAnim_EnergyIcon_Colorless,
};

static const struct SpriteTemplate sSpriteTemplate_EnergyIcons =
{
    .tileTag = TAG_ENERGY_ICONS,
    .paletteTag = TAG_ENERGY_ICONS,
    .oam = &sOamData_EnergyIcons,
    .anims = sSpriteAnimTable_EnergyIcons,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCallbackDummy
};

static const struct CompressedSpriteSheet sSpriteSheet_EnergyIcons =
{
    .data = sEnergyIcons_Gfx,
    .size = 9 * 4 * 32,  // 9 icons, 4 tiles each (16x16), 32 bytes per tile
    .tag = TAG_ENERGY_ICONS,
};

static const struct SpritePalette sSpritePalette_EnergyIcons =
{
    .data = sEnergyIcons_Pal,
    .tag = TAG_ENERGY_ICONS,
};

// Initialize energy icons (call once during battle setup)
static void LoadEnergyIconsGfx(void)
{
    LoadCompressedSpriteSheet(&sSpriteSheet_EnergyIcons);
    LoadSpritePalette(&sSpritePalette_EnergyIcons);
}

// Destroy all energy icon sprites
static void DestroyEnergyIcons(void)
{
    u8 i;
    for (i = 0; i < MAX_ENERGY_ICONS; i++)
    {
        if (sEnergyIconSpriteIds[i] != 0xFF)
        {
            DestroySprite(&gSprites[sEnergyIconSpriteIds[i]]);
            sEnergyIconSpriteIds[i] = 0xFF;
        }
    }
}

// Create energy icon sprites based on card data
static void DisplayEnergyIcons(const struct CardMoveData *cardData, u8 startX, u8 startY)
{
    u8 iconIndex = 0;
    u8 currentX = startX;
    u8 i;
    
    // Destroy any existing icons first
    DestroyEnergyIcons();
    
    // Helper macro to create icons
    #define CREATE_ENERGY_ICONS(count, type) \
        for (i = 0; i < (count) && iconIndex < MAX_ENERGY_ICONS; i++) \
        { \
            sEnergyIconSpriteIds[iconIndex] = CreateSprite(&sSpriteTemplate_EnergyIcons, currentX, startY, 1); \
            StartSpriteAnim(&gSprites[sEnergyIconSpriteIds[iconIndex]], type); \
            currentX += 12; /* 16 pixel icon with -4 overlap */ \
            iconIndex++; \
        }
    
    // Create icons for each energy type
    CREATE_ENERGY_ICONS(cardData->grassEnergyNeeded, ENERGY_ICON_GRASS);
    CREATE_ENERGY_ICONS(cardData->fireEnergyNeeded, ENERGY_ICON_FIRE);
    CREATE_ENERGY_ICONS(cardData->waterEnergyNeeded, ENERGY_ICON_WATER);
    CREATE_ENERGY_ICONS(cardData->electricEnergyNeeded, ENERGY_ICON_ELECTRIC);
    CREATE_ENERGY_ICONS(cardData->psychicEnergyNeeded, ENERGY_ICON_PSYCHIC);
    CREATE_ENERGY_ICONS(cardData->fightingEnergyNeeded, ENERGY_ICON_FIGHTING);
    CREATE_ENERGY_ICONS(cardData->darknessEnergyNeeded, ENERGY_ICON_DARKNESS);
    CREATE_ENERGY_ICONS(cardData->metalEnergyNeeded, ENERGY_ICON_METAL);
    
    // Calculate and display colorless energy
    u8 coloredEnergy = cardData->grassEnergyNeeded + cardData->fireEnergyNeeded + 
                      cardData->waterEnergyNeeded + cardData->electricEnergyNeeded + 
                      cardData->psychicEnergyNeeded + cardData->fightingEnergyNeeded + 
                      cardData->darknessEnergyNeeded + cardData->metalEnergyNeeded;
    u8 colorlessEnergy = cardData->energyNeeded - coloredEnergy;
    CREATE_ENERGY_ICONS(colorlessEnergy, ENERGY_ICON_COLORLESS);
    
    #undef CREATE_ENERGY_ICONS
}
```

## Step 4: Modify MoveSelectionDisplayMoveType

Replace the letter-based display with sprite creation:

```c
static void MoveSelectionDisplayMoveType(u32 battler)
{
    u8 *txtPtr, *end;
    u32 speciesId = gBattleMons[battler].species;
    struct ChooseMoveStruct *moveInfo = (struct ChooseMoveStruct *)(&gBattleResources->bufferA[battler][4]);
    u32 move = moveInfo->moves[gMoveSelectionCursor[battler]];
    
    // Check if this move has card data - display energy icon sprites
    if (gMovesInfo[move].card != NULL)
    {
        const struct CardMoveData *cardData = gMovesInfo[move].card;
        
        // Clear the TYPE window area
        gDisplayedStringBattle[0] = EOS;
        BattlePutTextOnWindow(gDisplayedStringBattle, B_WIN_MOVE_TYPE);
        
        // Display energy icons as sprites
        // X=208, Y=80 is approximately where the TYPE/ text area is
        // Adjust these coordinates to match your battle UI layout
        DisplayEnergyIcons(cardData, 208, 80);
        return;
    }
    
    // Normal type display for non-card moves...
    // (rest of existing code)
}
```

## Step 5: Initialize and cleanup

In battle initialization (e.g., `BattleMainCB1` or similar):
```c
LoadEnergyIconsGfx();
```

Initialize sprite IDs:
```c
u8 i;
for (i = 0; i < MAX_ENERGY_ICONS; i++)
    sEnergyIconSpriteIds[i] = 0xFF;
```

When changing moves or leaving move selection:
```c
DestroyEnergyIcons();
```

## Notes

- Adjust sprite positions (X, Y coordinates) to match your UI layout
- The spacing between icons (12 pixels with 4 pixel overlap) can be adjusted
- Maximum of 8 icons will be displayed to prevent overflow
- Icons are created left-to-right in the order: Grass, Fire, Water, Electric, Psychic, Fighting, Darkness, Metal, Colorless
- Consider adding priority/layering if icons overlap with other UI elements
