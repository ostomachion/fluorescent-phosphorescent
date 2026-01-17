# Species Info JSON Schema

This schema defines the structure for Pokémon species data in JSON format.

## Root Structure

```json
{
  "SPECIES_NAME": { /* SpeciesInfo */ },
  "ANOTHER_SPECIES": { /* SpeciesInfo */ }
}
```

## SpeciesInfo Fields

### Base Stats (all numeric)
```json
"baseStats": {
  "hp": 80,
  "attack": 82,
  "defense": 83,
  "speed": 80,
  "spAttack": 100,
  "spDefense": 100
}
```

### Type Information
```json
"types": { "raw": "MON_TYPES(TYPE_GRASS, TYPE_POISON)" },
"forceTeraType": { "raw": "TYPE_STELLAR" }  // Optional
```

### Catch/Experience
```json
"catchRate": 45,          // Numeric
"expYield": 236           // Numeric (or { "raw": "VENUSAUR_EXP_YIELD" })
```

### EV Yield (0-3 for each stat)
```json
"evYield": {
  "hp": 0,
  "attack": 0,
  "defense": 0,
  "speed": 0,
  "spAttack": 2,
  "spDefense": 1
}
```

### Items
```json
"itemCommon": { "raw": "ITEM_MIRACLE_SEED" },  // Omit if none
"itemRare": { "raw": "ITEM_MIRACLE_SEED" }     // Omit if none
```

### Breeding
```json
"genderRatio": { "raw": "PERCENT_FEMALE(12.5)" },
"eggCycles": 20,                                    // Numeric
"friendship": { "raw": "STANDARD_FRIENDSHIP" },     // Raw constant or numeric
"growthRate": { "raw": "GROWTH_MEDIUM_SLOW" },
"eggGroups": { "raw": "MON_EGG_GROUPS(EGG_GROUP_MONSTER, EGG_GROUP_GRASS)" }
```

### Abilities
```json
"abilities": { "raw": "{ ABILITY_OVERGROW, ABILITY_NONE, ABILITY_CHLOROPHYLL }" },
"safariZoneFleeRate": 0  // Numeric
```

### Pokédex Data
```json
"speciesName": "Venusaur",  // String → _("Venusaur")
"categoryName": "Seed",      // String → _("Seed")
"cryId": { "raw": "CRY_VENUSAUR" },
"natDexNum": { "raw": "NATIONAL_DEX_VENUSAUR" },  // Or numeric: 3
"height": 20,                // Decimeters (numeric)
"weight": 1000,              // Hectograms (numeric)
"description": "Venusaur's flower is said to take on vivid colors if it gets plenty of nutrition and sunlight. The flower's aroma soothes the emotions of people.",  // String → COMPOUND_STRING with proper formatting
"bodyColor": { "raw": "BODY_COLOR_GREEN" }
"pokemonScale": 256,            // Numeric
"pokemonOffset": 0,             // Numeric
"trainerScale": 388,            // Numeric
"trainerOffset": 6              // Numeric
```

### Graphics - Front Sprite
```json
"frontPic": { "raw": "gMonFrontPic_Venusaur" },
"frontPicSize": { "raw": "MON_COORDS_SIZE(64, 64)" },
"frontPicYOffset": 3,  // Numeric
"frontAnimFrames": { "raw": "ANIM_FRAMES(\n    ANIMCMD_FRAME(0, 10),\n    ANIMCMD_FRAME(1, 25),\n    ANIMCMD_FRAME(0, 10)\n)" },
"frontAnimId": { "raw": "ANIM_ROTATE_UP_SLAM_DOWN" },
"frontAnimDelay": 0,  // Numeric
"backAnimId": { "raw": "BACK_ANIM_SHAKE_GLOW_GREEN" }
```

### Graphics - Back Sprite
```json
"backPic": { "raw": "gMonBackPic_Venusaur" },
"backPicSize": { "raw": "MON_COORDS_SIZE(64, 48)" },
"backPicYOffset": 10  // Numeric
```

### Graphics - Palettes & Icons
```json
"palette": { "raw": "gMonPalette_Venusaur" },
"shinyPalette": { "raw": "gMonShinyPalette_Venusaur" },
"iconSprite": { "raw": "gMonIcon_Venusaur" },
"iconPalIndex": 1,  // 0-7 numeric
"noFlip": 0         // 0 or 1 (boolean as numeric)
```

### Graphics - Female Differences (optional)
```json
"frontPicFemale": { "raw": "gMonFrontPic_VenusaurF" },
"backPicFemale": { "raw": "gMonBackPic_VenusaurF" },
"frontPicSizeFemale": { "raw": "MON_COORDS_SIZE(64, 64)" },
"backPicSizeFemale": { "raw": "MON_COORDS_SIZE(64, 48)" },
"paletteFemale": { "raw": "gMonPalette_VenusaurF" },
"shinyPaletteFemale": { "raw": "gMonShinyPalette_VenusaurF" },
"iconSpriteFemale": { "raw": "gMonIcon_VenusaurF" },
"iconPalIndexFemale": 1
```

### Graphics - Footprint (optional)
```json
"footprint": { "raw": "FOOTPRINT(Venusaur)" }
```

### Battle Display
```json
"enemyMonElevation": 0,     // Numeric (how high above ground)
"pokemonJumpType": 0        // Numeric (0-3)
```

### Shadow Settings
```json
"enemyShadow": { "raw": "SHADOW(0, 5, SHADOW_SIZE_M)" }  // Omit to use defaults
```

### Flags (all numeric 0 or 1)
```json
"isLegendary": 0,
"isMythical": 0,
"isUltraBeast": 0,
"isParadox": 0,
"isTotem": 0,
"isMegaEvolution": 0,
"isPrimalReversion": 0,
"isUltraBurst": 0,
"isGigantamax": 0,
"isTeraForm": 0,
"isAlolanForm": 0,
"isGalarianForm": 0,
"isHisuianForm": 0,
"isPaldeanForm": 0,
"cannotBeTraded": 0,
"perfectIVCount": 0,      // 0-7
"dexForceRequired": 0,
"tmIlliterate": 0,
"isFrontierBanned": 0
```

### Move/Evolution Data
```json
"levelUpLearnset": { "raw": "sVenusaurLevelUpLearnset" },
"teachableLearnset": { "raw": "sVenusaurTeachableLearnset" },
"eggMoveLearnset": { "raw": "sVenusaurEggMoveLearnset" },  // Omit if none
"evolutions": { "raw": "EVOLUTION({EVO_LEVEL, 32, SPECIES_VENUSAUR})" },  // Omit if none
"formSpeciesIdTable": { "raw": "sVenusaurFormSpeciesIdTable" },  // Omit if none
"formChangeTable": { "raw": "sVenusaurFormChangeTable" }  // Omit if none
```

### Overworld Data (optional)
```json
"overworld": { "raw": "OVERWORLD(\n    sPicTable_Venusaur,\n    SIZE_32x32,\n    SHADOW_SIZE_M,\n    TRACKS_FOOT,\n    sAnimTable_Following,\n    gOverworldPalette_Venusaur,\n    gShinyOverworldPalette_Venusaur\n)" },
"overworldFemale": { "raw": "OVERWORLD_FEMALE(\n    sPicTable_VenusaurF,\n    SIZE_32x32,\n    SHADOW_SIZE_M,\n    TRACKS_FOOT,\n    sAnimTable_Following\n)" }
```

### Form Inheritance
```json
"additionalForms": {
  "MEGA": {
    // Same structure as SpeciesInfo, but only include fields that differ
    "baseStats": {
      "attack": 100,
      "defense": 123,
      "spAttack": 122,
      "spDefense": 120
    },
    "flags": {
      "megaEvolution": true
    }
    // Everything else inherited from base VENUSAUR
  }
}
```

## Value Types

1. **Numbers**: Plain JSON numbers
   - Examples: `45`, `236`, `1000`, `0`, `1`
   - Used for: baseStats, catchRate, height, weight, offsets, indices, flags

2. **Strings**: Plain JSON strings → converted to `_("string")`
   - Examples: `"Venusaur"`, `"Seed"`
   - Used for: speciesName, categoryName

3. **Descriptions**: Plain JSON strings → converted to `COMPOUND_STRING()` with proper line breaks
   - Example: `"This is a description that will be word-wrapped properly."`
   - Used for: description field

4. **Raw C code**: `{ "raw": "C_CODE_HERE" }` → output literally
   - Examples: `{ "raw": "ABILITY_OVERGROW" }`, `{ "raw": "MON_TYPES(TYPE_GRASS, TYPE_POISON)" }`
   - Used for: constants, macro calls, array initializers, any C expression
   - Allows preprocessor directives if needed

## Notes

- **Omit optional fields**: If a field isn't present in JSON, it won't be output to C (uses C struct's default/zero)
- **Conditionals**: For v1, resolve all conditionals before generating JSON based on chosen config values
- **Inheritance**: Forms/variants only need to specify fields that differ from the base
- **Start with raw**: Initially, most fields will be `{ "raw": "..." }`. As we refine, we can convert more fields to structured formats

## Field Mapping (C struct field → JSON key)

For reference, here's the complete mapping:
- `baseHP` → `baseStats.hp`
- `baseAttack` → `baseStats.attack`
- `baseDefense` → `baseStats.defense`
- `baseSpeed` → `baseStats.speed`
- `baseSpAttack` → `baseStats.spAttack`
- `baseSpDefense` → `baseStats.spDefense`
- `types` → `types` (as MON_TYPES macro)
- `catchRate` → `catchRate`
- `forceTeraType` → `forceTeraType`
- `expYield` → `expYield`
- `evYield_HP` → `evYield.hp`
- `evYield_Attack` → `evYield.attack`
- etc. (see struct for complete list)
