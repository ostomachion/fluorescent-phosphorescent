# Species Info JSON Integration

## Overview

This directory contains species data that can be managed via JSON as the source of truth. The pipeline supports:
- **Extraction**: C headers → JSON (`tools/species_to_json.py`)
- **Generation**: JSON → C headers (via `json_data_rules.mk`)
- **Template**: Inja template (`families.json.txt`)
- **Optimization**: Preprocessor block grouping (`tools/jsonproc_with_grouping.py`)

## Current Status

⚠️ **JSON is ~83% complete** - The extraction tool successfully parses 1,341 of 1,611 species (83.2%).

The remaining 270 entries need manual work:
- **Macro-based species** (e.g., Unown forms) - use complex macros that can't be auto-parsed
- **Complex conditionals** - fields with multiple `#if/#elif/#else` branches (e.g., `expYield`)
- **Incomplete data** - parsing failed for various reasons
- **Placeholders** - detected but have no data

**Post-processing status**: Simple conditionals (e.g., `frontPicFemale` with single `#if/#endif`) are converted to clean `field + field_condition` structure. Complex conditionals with `#elif` or `#else` are kept as `{"raw": "..."}` blocks.

Until the JSON is 100% complete, **the .h files remain the source of truth**.

## When JSON is Complete

Once all 270 missing entries are manually added to the JSON files:

1. **Auto-regeneration** is already configured in `json_data_rules.mk`
2. **Touching a JSON file** will trigger regeneration of its corresponding .h file
3. **The build will use JSON as source of truth**

### Manual Regeneration

To manually regenerate all headers from JSON:

```bash
for gen in 1 2 3 4 5 6 7 8 9; do
  python3 tools/jsonproc_with_grouping.py \
    src/data/pokemon/species_info/gen_${gen}_families.json \
    src/data/pokemon/species_info/families.json.txt \
    src/data/pokemon/species_info/gen_${gen}_families.h
done
```

### Re-extraction from C Headers

To extract fresh JSON from the current .h files (with post-processing):

```bash
for gen in 1 2 3 4 5 6 7 8 9; do
  # Extract to raw JSON
  python3 tools/species_to_json.py \
    src/data/pokemon/species_info/gen_${gen}_families.h \
    /tmp/gen_${gen}_raw.json
  
  # Post-process: convert simple conditionals to clean structure
  python3 tools/json_postprocess.py \
    /tmp/gen_${gen}_raw.json \
    src/data/pokemon/species_info/gen_${gen}_families.json
done
```

**What post-processing does:**
- Converts simple `#if COND\nVALUE\n#endif` → `{"field": "VALUE", "field_condition": "COND"}`
- Keeps complex conditionals with `#elif`/`#else` as `{"raw": "..."}` blocks
- Parses `MON_COORDS_SIZE(w, h)` into `{"width": w, "height": h}` objects

## File Structure

- `gen_*_families.h` - C header files (current source of truth)
- `gen_*_families.json` - JSON data files (83% complete, extracted from .h)
- `families.json.txt` - Inja template for generation
- `test_families.h/.json/.json.txt` - Test/example files

## Tools

- `tools/species_to_json.py` - Extracts JSON from C headers
- `tools/json_postprocess.py` - Post-processes raw blocks to clean structure (not currently used - causes issues with multi-line conditionals)
- `tools/jsonproc_with_grouping.py` - Generates C from JSON with preprocessor optimization
- `json_data_rules.mk` - Make rules for auto-regeneration

## Next Steps

To complete the JSON:

1. Review the extraction warnings for each generation
2. Manually add the missing species to JSON files  
3. Test regeneration: `make clean && make -j16`
4. Verify in-game functionality
5. Commit as source of truth

See `docs/PREPROCESSOR_FIX.md` for details on the conditional field handling.
