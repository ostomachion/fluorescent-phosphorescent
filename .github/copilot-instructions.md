# Copilot Coding Agent Instructions for fluorescent-phosphorescent

## Project Overview
**fluorescent-phosphorescent** is a Pokemon Emerald ROM hack that is replacing the battle system with the Pokemon TCG Pocket system (a simplified TCG game). It's based on pokeemerald-expansion, which is a comprehensive ROM hack toolkit built on the pret pokeemerald decompilation.

**Key Project Facts:**
- **Language:** C (with some ARM assembly)
- **Target Platform:** Game Boy Advance (GBA)
- **Build System:** GNU Make with custom toolchain (arm-none-eabi-gcc)
- **Size:** ~162,000+ lines of battle-related C code, ~25MB ROM when built
- **Type:** ROM hack / Game development project
- **Testing:** Integrated test runner system (mgba-rom-test)

## Critical Development Principle: APPEND, DON'T MODIFY

**When adding new TCG Pocket mechanics or content to this codebase:**
1. **Keep old code around** - Do not remove or replace existing Pokemon battle system code
2. **Add new fields incrementally** - For example, add `.cardData` structures rather than reusing existing fields
3. **Mark all custom changes** - Wrap new TCG Pocket code with comments like:
   ```c
   // [TCG_POCKET_START] - Custom code for TCG Pocket battle system
   // Your new code here
   // [TCG_POCKET_END]
   ```
4. **Allow both systems to coexist** - The battle system should check if TCG data exists for a Pokemon/move before using it
5. **Why:** This prevents breaking the existing system, allows incremental development, and makes it clear what can be modified vs what should be preserved

## Build System

### Prerequisites (ALWAYS install these first)
```bash
sudo apt update
sudo apt install -y binutils-arm-none-eabi gcc-arm-none-eabi libnewlib-arm-none-eabi libpng-dev python3
```

### Build Commands (tested and verified)

**Standard Build (3-4 minutes on 4-core system):**
```bash
make -j$(nproc)
# Output: pokeemerald.gba (32MB ROM file)
# Memory usage shown: EWRAM ~86%, IWRAM ~87%, ROM ~74%
```

**Clean Build:**
```bash
make clean    # Clean build artifacts
make tidy     # More thorough clean, removes all build outputs
```

**Release Build:**
```bash
make tidy
make -j$(nproc) release
# Output: pokeemerald-release.gba
```

**Test Build (10-15 minutes, VERY SLOW):**
```bash
make -j$(nproc) check
# Runs comprehensive battle mechanics tests via mgba-rom-test
# Tests located in test/battle/ directory
```

**Debug Build:**
```bash
make debug
# Adds -Og -g flags for debugging
```

### Build Targets
- `make` or `make all` - Build standard ROM
- `make rom` - Same as all
- `make check` - Build and run tests  
- `make release` - Optimized release build
- `make debug` - Debug build with symbols
- `make clean` - Remove build artifacts
- `make tidy` - Remove all generated files
- `make tools` - Build only the toolchain utilities

### Important Build Notes
- **Parallel builds are critical:** Always use `-j$(nproc)` for reasonable build times
- **Build artifacts:** Output goes to `build/emerald/` directory
- **First build takes longer:** Tools are compiled first time only
- **Incremental builds work:** Make tracks dependencies properly

## Testing System

### Test Infrastructure
- **Location:** `test/` directory
- **Battle Tests:** `test/battle/` with extensive subdirectories:
  - `ability/` - Ability-specific tests (300+ files)
  - `move_effect/` - Move effect tests (300+ files)  
  - `ai/` - AI behavior tests
  - `form_change/`, `gimmick/`, `hold_effect/`, etc.
- **Test Runner:** Custom system in `test/test_runner.c` (3500+ lines)
- **Framework:** Uses mgba-rom-test-hydra for automated testing

### Running Tests
```bash
# Run all tests (SLOW - 10-15+ minutes)
make -j$(nproc) check

# Tests are comprehensive and validate:
# - Move effects and interactions
# - Ability behaviors
# - Item effects
# - Battle mechanics
# - AI decision making
```

### Test Guidelines
- Tests use custom DSL-like syntax (see `test/battle/*.c`)
- Each test simulates battle scenarios
- Use `ASSUMPTIONS`, `GIVEN`, `WHEN`, `THEN` structure
- Reference existing tests in `test/battle/` for patterns

## Repository Structure

### Core Battle System Files (PRIMARY FOCUS)
```
src/battle_*.c               - 90+ battle system files (~163k lines total)
├── battle_main.c            - Main battle loop (6100 lines)
├── battle_script_commands.c - Battle scripting engine (15.6k lines)
├── battle_util.c            - Core battle utilities (12.3k lines)
├── battle_ai_main.c         - AI decision making (7000 lines)
├── battle_ai_util.c         - AI utilities (6400 lines)
└── battle_*.c               - Animations, controllers, effects, etc.

include/battle*.h            - 50+ battle-related headers
include/constants/battle*.h  - Battle constants and enums
```

### Configuration System (include/config/)
```
include/config/
├── battle.h          - Battle mechanics toggles
├── ai.h             - AI behavior configs
├── caps.h           - Level/stat cap configs
├── debug.h          - Debug feature toggles
├── general.h        - General game configs
├── pokemon.h        - Pokemon data configs
├── item.h           - Item behavior configs
└── species_enabled.h - Toggle species on/off
```

**Config Philosophy:** Features use runtime checks (e.g., `if (B_FEATURE_FLAG)`) rather than `#ifdef`

### Data Files
```
data/
├── battle_scripts_*.s     - Battle script data
├── maps/                  - 900+ map files
├── layouts/              - 800+ layout files
└── scripts/              - Event scripts

src/data/               - Embedded data in C
graphics/              - 60+ sprite/graphic directories
sound/                 - Audio assets
```

### Key Directories
```
/
├── Makefile               - Main build configuration (550 lines)
├── README.md             - Project overview
├── INSTALL.md            - Installation instructions  
├── CONTRIBUTING.md       - Contribution guidelines
├── FEATURES.md           - Feature list (extensive)
├── src/                  - 300+ C source files
├── include/              - 200+ header files
├── asm/                  - Assembly code
├── data/                 - Game data
├── graphics/             - Sprites and graphics
├── test/                 - Test infrastructure
├── tools/                - Build tools (20+ utilities)
├── docs/                 - Documentation (mdbook)
├── constants/            - Constant definitions
└── dev_scripts/          - Development utilities
```

## GitHub Actions / CI

### Workflows (.github/workflows/)

**build.yml (CI Pipeline):**
```yaml
Runs on: push to master/upcoming, pull requests
Steps:
  1. Install: binutils-arm-none-eabi, gcc-arm-none-eabi, libnewlib-arm-none-eabi, libpng-dev, python3
  2. Build ROM: make -j${nproc} -O all
  3. Release Build: make tidy && make -j${nproc} release  
  4. Test: make -j${nproc} check (TEST=1)
  
Environment:
  UNUSED_ERROR=1         # Treat unused warnings as errors
  DEPRECATED_ERROR=1     # Treat deprecated warnings as errors
```

**docs.yml:**
- Builds mdbook documentation from `docs/`
- Deploys to GitHub Pages (if enabled)

**Important:** CI requires ALL THREE steps to pass (ROM build, release build, tests)

## Common Issues & Solutions

### Build Issues
1. **"arm-none-eabi-gcc: command not found"**
   - Install toolchain: `sudo apt install binutils-arm-none-eabi gcc-arm-none-eabi libnewlib-arm-none-eabi`

2. **Build hangs or is extremely slow**
   - Use parallel make: `make -j$(nproc)` (NOT just `make`)
   - First build takes longer (tools compilation)

3. **Linker warnings about RWX permissions**
   - Expected/normal for GBA development, can be ignored

### Test Issues
1. **Tests timing out**
   - Tests take 10-15+ minutes, be patient
   - Only run full test suite before final submission

2. **Test-specific build**
   - Tests require separate build: `make -j$(nproc) check`
   - Test executable: `pokeemerald-test.elf`

## File Organization Best Practices

### Battle System Architecture
1. **Core Logic:** `src/battle_*.c` files handle game mechanics
2. **Scripting:** `data/battle_scripts_*.s` define battle sequences  
3. **Constants:** `include/constants/battle*.h` define enums/flags
4. **Configuration:** `include/config/battle.h` controls features

### Adding New Features
1. Check if config flag exists in `include/config/`
2. Add data structures to appropriate `include/*.h`
3. Implement logic in `src/*.c`
4. Add battle scripts if needed in `data/`
5. Add tests in `test/battle/`
6. **Remember:** Mark TCG Pocket changes with comments!

## Code Style (CRITICAL - See docs/STYLEGUIDE.md)

### Naming Conventions
- Functions/Structs: `PascalCase`
- Variables/Fields: `camelCase`  
- Global variables: `gVariableName`
- Static variables: `sVariableName`
- Constants/Macros: `CAPS_WITH_UNDERSCORES`

### Formatting
- **Indentation:** 4 spaces (NOT tabs) for C files
- **Braces:** Opening brace on next line for control structures
- **Comments:** Single-line (`//`) for brief notes, block (`/* */`) for in-depth
- Loop iterators: Declare in loop (`for (u32 i = 0; ...`)

### Data Types
- Use `u32`/`s32` for general variables
- Use smallest type for saveblock data, EWRAM, globals
- Use enums for sequential constants (not in saveblock)
- Type-check enums: `enum Gimmick gimmick` not `u32 gimmick`

## Documentation Resources

- **Online Docs:** https://rh-hideout.github.io/pokeemerald-expansion/
- **README:** Overview and getting started
- **INSTALL.md:** Detailed installation for all platforms
- **CONTRIBUTING.md:** PR process and guidelines  
- **FEATURES.md:** Complete feature list
- **docs/STYLEGUIDE.md:** Code style requirements (MUST FOLLOW)

## Special Tools

### Included Utilities (tools/)
- `gbagfx` - Graphics conversion
- `jsonproc` - JSON data processing
- `mapjson` - Map data tools
- `scaninc` - Dependency scanning
- `mid2agb` - MIDI to GBA audio
- `learnset_helpers` - Move data generation
- `mgba-rom-test-hydra` - Test runner

### External Tools (Recommended)
- **Porymap:** Map editor (https://github.com/huderlem/porymap)
- **Poryscript:** Scripting language (https://github.com/huderlem/poryscript)

## Memory Constraints

**GBA Memory Regions (from build output):**
- **EWRAM:** 256 KB (typically ~86-92% used)
- **IWRAM:** 32 KB (typically ~86-93% used)  
- **ROM:** 32 MB max (typically ~74-77% used)

**Implication:** Be mindful of memory usage, especially in EWRAM/IWRAM

## Quick Reference Checklist

Before making changes:
- [ ] Install toolchain dependencies
- [ ] Run `make -j$(nproc)` to verify clean build
- [ ] Understand which battle system files are involved
- [ ] Check relevant config flags in `include/config/`
- [ ] Review similar existing code for patterns

After making changes:
- [ ] Follow code style guide (indentation, naming, etc.)
- [ ] Mark TCG Pocket changes with `[TCG_POCKET_START/END]` comments
- [ ] Build with `make -j$(nproc)` to verify
- [ ] Add/update tests if adding mechanics
- [ ] Run `make -j$(nproc) check` before final submission
- [ ] Verify UNUSED_ERROR and DEPRECATED_ERROR compliance

## Trust These Instructions

These instructions have been validated through:
1. Successful clean build from scratch
2. Installation of all dependencies  
3. Verification of build times and outputs
4. Testing of build variants (debug, release, test)
5. Review of CI pipeline configuration
6. Analysis of codebase structure and conventions

**Only search/explore further if:**
- Information here is incomplete for your specific task
- You encounter an error not documented above
- You need details about a specific subsystem not covered

---
*Document Version: 1.0 - Created via comprehensive repository analysis*
