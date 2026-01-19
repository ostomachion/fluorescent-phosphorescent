# Species Info JSON System Guide

## Overview
Species data is now stored in JSON format and automatically converted to C header files during the build process. This makes species data easier to edit, maintain, and version control.

## File Locations

### Source Files (Edit These)
- **JSON data**: `src/data/pokemon/species_info/gen_*_families.json` (9 files, one per generation)
- **Template**: `src/data/pokemon/species_info/families.json.txt` (Inja template)

### Generated Files (Do Not Edit Manually)
- **C headers**: `src/data/pokemon/species_info/gen_*_families.h` (auto-generated)

## How It Works

1. **Edit JSON files** - Modify species data in `gen_*_families.json`
2. **Run build** - Run `make` to regenerate headers
3. **Headers updated** - Build system automatically regenerates `.h` files from JSON

## JSON Format

### Simple Values
```json
{
  "PIKACHU": {
    "baseHP": 35,
    "baseAttack": 55,
    "baseDefense": 40
  }
}
```

### Generation-Aware Values
For stats that changed across generations, use this format:
```json
{
  "MAGCARGO": {
    "baseSpAttack": {
      "gen7": 90,
      "gen6": 80
    }
  }
}
```

**How it works:**
- The template generates: `P_UPDATED_STATS >= GEN_7 ? 90 : (P_UPDATED_STATS >= GEN_6 ? 80 : (80))`
- Smart fallback uses the **lowest-numbered generation** as the default value
- Supports ANY combination of gen1-gen9

### Forms
```json
{
  "ALAKAZAM": {
    "baseHP": 55,
    "forms": {
      "MEGA": {
        "baseHP": 55,
        "baseSpDefense": {
          "gen7": 105,
          "gen6": 95
        }
      }
    }
  }
}
```

## Build Commands

### Normal Build (Regenerates All)
```bash
make
```

### Regenerate Specific Generation
```bash
make src/data/pokemon/species_info/gen_1_families.h
```

### Force Regenerate All Families
```bash
rm src/data/pokemon/species_info/gen_*_families.h
make
```

### Clean Build
```bash
make clean
make -j$(nproc)
```

## Adding Missing Species

If you encounter species that couldn't be auto-parsed:

1. Open the appropriate generation JSON file
2. Find the species entry (or add a new one)
3. Fill in the missing fields using the format above
4. Run `make` to regenerate

## Tips

### Finding Species
- Gen 1: Original 151 + forms (Megas, Gigantamax, etc.)
- Gen 2: Johto Pokémon (Chikorita to Celebi)
- Gen 3: Hoenn Pokémon (Treecko to Deoxys)
- Gen 4: Sinnoh Pokémon (Turtwig to Arceus)
- Gen 5: Unova Pokémon (Victini to Genesect)
- Gen 6: Kalos Pokémon (Chespin to Volcanion)
- Gen 7: Alola Pokémon (Rowlet to Melmetal)
- Gen 8: Galar Pokémon (Grookey to Eternatus)
- Gen 9: Paldea Pokémon (Sprigatito to Pecharunt)

### Common Fields
- **Base Stats**: `baseHP`, `baseAttack`, `baseDefense`, `baseSpeed`, `baseSpAttack`, `baseSpDefense`
- **Experience**: `expYield` (can be generation-aware)
- **Types**: `types` (array, e.g., `["fire", "flying"]`)
- **Abilities**: `abilities` (array of up to 3)
- **Egg Groups**: `eggGroups` (array)
- **Gender Ratio**: `genderRatio` (object with `female` percentage)
- **Growth Rate**: `growthRate` (e.g., `"medium-slow"`)

### Raw C Expressions
For complex values that need to be C code:
```json
{
  "PIKACHU": {
    "expYield": {
      "raw": "#if P_UPDATED_EXP_YIELDS >= GEN_8\n300\n#else\n200\n#endif"
    }
  }
}
```

## Statistics

- **Total species**: 1,546 across all generations
- **Generation-aware stats**: 789 fields with conditional values
- **Empty values**: 0 (all validated)
- **Template features**: Smart fallback, supports gen1-gen9, proper Inja syntax

## Troubleshooting

### Build fails after editing JSON
- Check JSON syntax (use a JSON validator)
- Ensure all required fields are present
- Check for typos in field names

### Generated headers look wrong
- Verify JSON format matches examples above
- Check template file hasn't been corrupted
- Try regenerating: `rm src/data/pokemon/species_info/gen_*_families.h && make`

### Species not appearing
- Check if species is in the correct generation file
- Verify the species name matches constants in `include/constants/species.h`

## Development Notes

- JSON files are ~2.9 MB total
- Generated headers are ~2.8 MB total
- Build time: ~3-5 minutes with `-j$(nproc)`
- Template uses Inja (https://github.com/pantor/inja)
- Build system integration via `json_data_rules.mk`
