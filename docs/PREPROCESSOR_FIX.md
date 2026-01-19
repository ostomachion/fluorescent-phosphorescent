# Preprocessor Conditional Handling - Solution Summary

## Problem
The original issue was that preprocessor conditionals (like `#if P_GENDER_DIFFERENCES`) were being stored as `{"raw": "#if COND\nVALUE\n#endif"}` in JSON, which is a hack. When output, they created malformed C code with wrong indentation.

## Solution
A clean 4-stage pipeline that properly separates concerns:

### 1. Extraction (`tools/species_to_json.py`)
- **Status**: Kept as-is (working correctly)
- Extracts C structs to JSON
- Stores preprocessor blocks as `{"raw": "#if COND\nVALUE\n#endif"}`
- This is appropriate at extraction time since we're parsing C code verbatim

### 2. Post-Processing (`tools/json_postprocess.py`)
- **Status**: Created and working
- Converts raw blocks into clean structure:
  - Input: `{"frontPicFemale": {"raw": "#if P_GENDER_DIFFERENCES && !P_GBA_STYLE_SPECIES_GFX\ngMonFrontPic_MeganiumF\n#endif"}}`
  - Output: `{"frontPicFemale": "gMonFrontPic_MeganiumF", "frontPicFemale_condition": "P_GENDER_DIFFERENCES && !P_GBA_STYLE_SPECIES_GFX"}`
- Also parses values into proper types (MON_COORDS_SIZE → {width, height})
- Recursively processes forms

### 3. Template (`src/data/pokemon/species_info/families.json.txt`)
- **Status**: Updated and working
- Checks for `fieldName_condition` suffix
- Outputs properly formatted code:
  ```c
  #if P_GENDER_DIFFERENCES && !P_GBA_STYLE_SPECIES_GFX
          .frontPicFemale = gMonFrontPic_MeganiumF,
  #endif //P_GENDER_DIFFERENCES && !P_GBA_STYLE_SPECIES_GFX
  ```
- Uses conditional indentation to ensure proper formatting

### 4. Grouping (`tools/jsonproc_with_grouping.py`)
- **Status**: Created and working
- Post-processes generated C to merge consecutive same-condition blocks
- Input:
  ```c
  #if P_GENDER_DIFFERENCES && !P_GBA_STYLE_SPECIES_GFX
          .frontPicFemale = value1,
  #endif //P_GENDER_DIFFERENCES && !P_GBA_STYLE_SPECIES_GFX
  #if P_GENDER_DIFFERENCES && !P_GBA_STYLE_SPECIES_GFX
          .backPicFemale = value2,
  #endif //P_GENDER_DIFFERENCES && !P_GBA_STYLE_SPECIES_GFX
  ```
- Output:
  ```c
  #if P_GENDER_DIFFERENCES && !P_GBA_STYLE_SPECIES_GFX
          .frontPicFemale = value1,
          .backPicFemale = value2,
  #endif //P_GENDER_DIFFERENCES && !P_GBA_STYLE_SPECIES_GFX
  ```

## JSON Structure

**Clean separation of data and metadata:**
```json
{
  "frontPicFemale": "gMonFrontPic_MeganiumF",
  "frontPicFemale_condition": "P_GENDER_DIFFERENCES && !P_GBA_STYLE_SPECIES_GFX",
  "frontPicSizeFemale": {"width": 48, "height": 64},
  "frontPicSizeFemale_condition": "P_GENDER_DIFFERENCES && !P_GBA_STYLE_SPECIES_GFX",
  "backPicFemale": "gMonBackPic_MeganiumF",
  "backPicFemale_condition": "P_GENDER_DIFFERENCES && !P_GBA_STYLE_SPECIES_GFX",
  "backPicSizeFemale": {"width": 56, "height": 64},
  "backPicSizeFemale_condition": "P_GENDER_DIFFERENCES && !P_GBA_STYLE_SPECIES_GFX"
}
```

**Benefits:**
- Values are clean and typed (not strings with embedded #if directives)
- Conditions are explicit metadata
- Easy to query, modify, and validate
- Template can output proper C with correct indentation
- Grouping can optimize output

## Usage Workflow

### Full Pipeline
```bash
# 1. Extract from C
python3 tools/species_to_json.py src/data/pokemon/species_info/gen_2_families.h gen_2.json

# 2. Post-process to clean structure
python3 tools/json_postprocess.py gen_2.json gen_2_clean.json

# 3. Generate C with grouping
python3 tools/jsonproc_with_grouping.py gen_2_clean.json src/data/pokemon/species_info/families.json.txt gen_2_families.h
```

### Or combined (for all gens):
```bash
for gen in 1 2 3 4 5 6 7 8 9; do
  python3 tools/species_to_json.py src/data/pokemon/species_info/gen_${gen}_families.h /tmp/gen_${gen}.json
  python3 tools/json_postprocess.py /tmp/gen_${gen}.json src/data/pokemon/species_info/gen_${gen}_families.json
  python3 tools/jsonproc_with_grouping.py src/data/pokemon/species_info/gen_${gen}_families.json src/data/pokemon/species_info/families.json.txt src/data/pokemon/species_info/gen_${gen}_families.h
done
```

## Design Principles Followed

1. **Separation of Concerns**: Each tool does one thing well
2. **No Hacks in Data**: JSON stores clean typed data, not raw C code
3. **Metadata is Explicit**: Conditions are stored separately as `_condition` suffixes
4. **Progressive Enhancement**: Each stage adds value without breaking previous stages
5. **Reversible**: Can go C → JSON → C without data loss

## Limitations & Future Work

- Extraction doesn't handle all macro patterns (COPY_FAMILY, UNOWN_MISC_INFO, etc.)
  - These result in placeholder entries in JSON
  - ~207 entries need manual addition
- Post-processor assumes simple #if/#endif structure
  - Doesn't handle #elif or nested conditions yet
  - Could be extended if needed
- Grouping is naive (checks exact condition match)
  - Could be smarter about logically equivalent conditions
  - Works well enough for current use case
