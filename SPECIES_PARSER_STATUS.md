# Species Parser Status Report

## Overall Coverage: 86.6% (1341/1548 species)

The parser successfully handles standard species definitions but cannot parse species that use macro-based definitions.

## Generation Breakdown

| Gen | Parsed | Total | Coverage | Missing Species |
|-----|--------|-------|----------|----------------|
| 1   | 277    | 277   | 100.0%   | ✓ None |
| 2   | 114    | 142   | 80.3%    | UNOWN (28 variants) |
| 3   | 173    | 173   | 100.0%   | ✓ None |
| 4   | 96     | 117   | 82.1%    | ARCEUS (18 types), MOTHIM (3 cloaks) |
| 5   | 193    | 198   | 97.5%    | GENESECT (5 drives) |
| 6   | 130    | 180   | 72.2%    | FURFROU (10), VIVILLON/SCATTERBUG/SPEWPA (60 total) |
| 7   | 111    | 143   | 77.6%    | MINIOR (14 colors), SILVALLY (18 types) |
| 8   | 123    | 186   | 66.1%    | ALCREMIE (63 decorations!) |
| 9   | 124    | 132   | 93.9%    | OGERPON (8 masks) |

**Total: 1341 parsed, 207 unparsed**

## Macro-Based Species (Require Special Handling)

These species use `#define SPECIES_MISC_INFO(...)` macros instead of standard struct definitions:

1. **UNOWN** (28 forms) - Uses `UNOWN_MISC_INFO` macro
2. **MOTHIM** (3 cloaks) - PLANT, SANDY, TRASH
3. **ARCEUS** (18 types) - One for each type
4. **GENESECT** (5 drives) - Different drive forms
5. **VIVILLON family** (60 total) - VIVILLON, SCATTERBUG, SPEWPA with 20 patterns each
6. **FURFROU** (10 trims) - Uses `FURFROU_MISC_INFO` macro
7. **MINIOR** (14 colors) - Uses `MINIOR_MISC_INFO` macro
8. **SILVALLY** (18 types) - One for each type
9. **ALCREMIE** (63!) - Combinations of sweets × cream colors
10. **OGERPON** (8 masks) - Different mask forms

## Safety Features

The parser now includes comprehensive safety checks:

✅ **Counts all species entries** in the C file (not just parseable ones)
✅ **Reports unparsed species** with ERROR level logging
✅ **Shows coverage percentage** for each file
✅ **Groups unparsed species** by prefix for easy identification
✅ **Validates parsed data** for empty or mostly-raw fields
✅ **Tracks parse errors** separately from macro-based species

## Example Output

```
ERROR: ============================================================
ERROR: UNPARSED SPECIES: 28 species entries found but not converted
ERROR: These likely use macros or non-standard formats:
ERROR:   - UNOWN: 28 variants (UNOWN, UNOWN_B, UNOWN_C, ...)
ERROR: ============================================================
WARNING: Coverage: 114/142 species (80.3%)
```

## Next Steps

For full JSON conversion support, would need to:
1. Parse macro definitions to extract field values
2. Expand macro invocations with their parameters
3. Handle parameterized field assignments

Alternatively, these ~200 species could be manually converted or kept in C format since they're mostly cosmetic variants with identical stats.
