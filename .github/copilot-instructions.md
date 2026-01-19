# GitHub Copilot Instructions for pokeemerald-expansion

## Project Overview
This project is based on **pokeemerald-expansion** from RHH (Rom Hacking Hideout), a comprehensive toolkit for creating Pokémon GBA ROM hacks built on top of pret's pokeemerald decompilation.

**Key Project Facts:**
- **Language:** C (with some ARM assembly)
- **Target Platform:** Game Boy Advance (GBA)
- **Build System:** GNU Make with arm-none-eabi-gcc toolchain
- **Size:** ~162,000+ lines of battle-related C code, ~26MB ROM when built
- **Custom Feature:** Card battle system (Fluorescent & Phosphorescent)

## Critical Development Principle: APPEND, DON'T MODIFY

**When adding new card battle mechanics or content to this codebase:**
1. **Keep old code around** - Do not remove or replace existing Pokémon battle system code
2. **Mark all custom changes** except trivial or small changes - Wrap new card battle code with comments like to identify perservation priority:
   ```c
   // [FLUOPHOS_START]
   // Your new code here
   // [FLUOPHOS_END]
   ```
4. **Allow both systems to coexist** - The battle system could check if card data exists for a Pokémon/move before using it for example
5. **Why:** This prevents breaking the existing system, allows incremental development, makes upstream merges easier, and clearly marks what can be modified vs what should be preserved

## Repository Remotes
- **`RHH`**: The upstream pokeemerald-expansion repository (https://github.com/rh-hideout/pokeemerald-expansion)
- **`origin`**: Your personal fork (https://github.com/ostomachion/fluorescent-phosphorescent)

## Updating from Upstream

Follow RHH's official update process:

1. **Check your current version**:
   ```bash
   # Find the latest version tag that's in your branch:
   git tag --merged HEAD | grep "expansion/1\." | sort -V | tail -1
   
   # Or check the CHANGELOG:
   head -20 docs/CHANGELOG.md
   ```

2. **Update incrementally** using version tags:
   - Recommended version progression: 1.6.2 → 1.7.4 → 1.8.3 → 1.9.4 → 1.10.3 → latest
   - Always update to the next minor version, not jump to latest
   - See available tags: `git ls-remote --tags RHH | grep "expansion/" | sed 's/.*expansion\///' | sort -V`

3. **Pull the target version**:
   ```bash
   git pull RHH expansion/X.Y.Z  # e.g., expansion/1.14.2
   # OR for latest unreleased changes:
   git pull RHH master
   ```

4. **Build after merging** to verify:
   ```bash
   make clean && make -j16
   ```

## Building the Project

### Prerequisites
Before building, ensure all dependencies are installed (assume installed, but use this if needed):
```bash
sudo apt update
sudo apt install -y binutils-arm-none-eabi gcc-arm-none-eabi libnewlib-arm-none-eabi libpng-dev python3
```

### Quick Build
```bash
make -j$(nproc)  # Linux/WSL - uses all available CPU cores
```
**Important:** Always use `-j$(nproc)` for parallel builds. Without it, builds take 10-15+ minutes instead of 3-4 minutes.

### Clean Build (when things break)
```bash
make clean && make -j$(nproc)  # Clean build artifacts
make tidy && make -j$(nproc)   # More thorough clean (removes all generated files)
```

### Build Targets
- `make` or `make all` - Build standard ROM (`pokeemerald.gba`)
- `make rom` - Same as all
- `make check` - Build and run tests (SLOW: 10-15+ minutes)
- `make release` - Optimized release build (`pokeemerald-release.gba`)
- `make debug` - Debug build with symbols (`-Og -g` flags)
- `make clean` - Remove build artifacts
- `make tidy` - Remove all generated files
- `make tools` - Build only the toolchain utilities

### Build Info
- Default target: `pokeemerald.gba` (modern ROM)
- Build output: `build/emerald/` directory
- ROM size: ~26MB
- First build takes longer (tools are compiled)
- Incremental builds work properly

### Memory Constraints (GBA)
- **EWRAM:** 256 KB (typically ~86-92% used)
- **IWRAM:** 32 KB (typically ~86-93% used)
- **ROM:** 32 MB max (typically ~74-77% used)

**Implication:** Be mindful of memory usage, especially in EWRAM/IWRAM.

### Common Build Issues
- **"arm-none-eabi-gcc: command not found"**: Install toolchain prerequisites (see above)
- **Missing types (u32, u8, etc.)**: Header include order issue - check that `#include "global.h"` is first
- **Struct incomplete type**: Missing struct definition, check includes
- **Link errors**: Usually means a function signature changed - rebuild from clean
- **Linker warnings about RWX permissions**: Expected/normal for GBA development, can be ignored

## Development Guidelines

### Code Style
Follow the existing code style in pokeemerald-expansion (see `docs/STYLEGUIDE.md` for complete reference).

**Naming Conventions:**
- Functions/Structs: `PascalCase`
- Variables/Fields: `camelCase`
- Global variables: `gVariableName`
- Static variables: `sVariableName`
- Constants/Macros: `CAPS_WITH_UNDERSCORES`

**Formatting:**
- **Indentation:** 4 spaces (NOT tabs) for C files
- **Braces:** Opening brace on next line for control structures
- **Comments:** Single-line (`//`) for brief notes, block (`/* */`) for in-depth
- Loop iterators: Declare in loop (`for (u32 i = 0; ...`)

**Data Types:**
- Use `u32`/`s32` for general variables (not `int`)
- Use smallest type for saveblock data, EWRAM, globals
- Use `enum` types where defined (e.g., `enum Move`, `enum Ability`, `enum Type`)
- Type-check enums: `enum Gimmick gimmick` not `u32 gimmick`
- All warnings are treated as errors (`-Werror`)

### Testing

pokeemerald-expansion has an extensive automated testing system for battle mechanics.

**Running Tests:**
```bash
# Run all tests
make check -j

# Run specific tests (e.g., all Spikes tests)
make check TESTS="Spikes"

# Build a test ROM to debug specific tests in mgba
make pokeemerald-test.elf TESTS="Spikes"
```

**Writing Tests:**
Tests follow a pattern: `GIVEN` (setup) → `WHEN` (actions) → `SCENE` (verify output).

Example test structure:
```c
SINGLE_BATTLE_TEST("Stun Spore inflicts paralysis")
{
    GIVEN {
        PLAYER(SPECIES_WOBBUFFET);
        OPPONENT(SPECIES_WOBBUFFET);
    } WHEN {
        TURN { MOVE(player, MOVE_STUN_SPORE); }
    } SCENE {
        ANIMATION(ANIM_TYPE_MOVE, MOVE_STUN_SPORE, player);
        MESSAGE("The opposing Wobbuffet is paralyzed!");
        STATUS_ICON(opponent, paralysis: TRUE);
    }
}
```

**Test Types:**
- `SINGLE_BATTLE_TEST` - 1v1 battles
- `DOUBLE_BATTLE_TEST` - 2v2 battles
- `AI_SINGLE_BATTLE_TEST` - Tests AI behavior
- `KNOWN_FAILING` - Mark tests that fail due to known bugs

**Best Practices:**
- Test player-visible outputs (animations, messages) rather than internal state
- Use `ASSUME` to document prerequisites (e.g., move types, effects)
- Use `PARAMETRIZE` to run multiple test variations
- Always add tests when fixing bugs or adding features
- See `docs/tutorials/how_to_testing_system.md` for complete reference

### Configuration Files
Configuration is in `include/config/*.h`:
- `battle.h` - Battle system settings
- `debug.h` - Debug features (disable for release)
- `overworld.h` - Overworld features (followers, etc.)
- `pokemon.h` - Pokémon data settings
- Many others - check the directory

## Branch Strategy

### RHH Branches
- **`master`**: Latest stable + bugfixes (recommended for development)
- **`upcoming`**: Latest features + functionality (less stable)
- **Version tags** (`expansion/X.Y.Z`): Stable releases

### Local Branch Strategy
- `main`: Your stable working branch
- Create feature branches for major changes: `git switch -c feature/name`
- Keep `main` clean and buildable

## Quick Reference Checklist

**Before making changes:**
- [ ] Install toolchain dependencies (if first time)
- [ ] Run `make -j$(nproc)` to verify clean build
- [ ] Understand which files are involved
- [ ] Check relevant config flags in `include/config/`
- [ ] Review similar existing code for patterns
- [ ] Remember: APPEND new card battle code, don't modify existing battle system

**After making changes:**
- [ ] Follow code style guide (4 spaces, naming conventions, etc.)
- [ ] Mark card battle changes with `[FLUOPHOS_START/END]` comments
- [ ] Build with `make -j$(nproc)` to verify compilation
- [ ] Add/update tests if adding mechanics (when relevant)
- [ ] Run `make check` before submitting (if time allows)
- [ ] Verify no unused variable/function warnings

## Resources

### Documentation
- Main docs: https://rh-hideout.github.io/pokeemerald-expansion/
- Features list: [FEATURES.md](FEATURES.md)
- Changelog: [docs/CHANGELOG.md](docs/CHANGELOG.md)
- Inja templating:[docs/tutorials/inja.md](docs/tutorials/inja.md)

### Tools
- **Porymap**: Map editor (https://github.com/huderlem/porymap)
- **Poryscript**: Scripting language (https://github.com/huderlem/poryscript)
- **Porytiles**: Tileset management (https://github.com/grunt-lucas/porytiles)
- **Tilemap Studio**: Tilemap editor (https://github.com/Rangi42/tilemap-studio)

### Community
- Discord: https://discord.gg/6CzjAG6GZk (Rom Hacking Hideout)
- Ask in `#expansion-dev` for development help
- Use `#pr-discussions` for feature discussions

## Common Tasks

### Adding a New Species
1. Add constant to `include/constants/species.h`
2. Add species info to `src/data/pokemon/species_info/*.h`
3. Add to form table in `src/data/pokemon/form_species_tables.h` (if needed)
4. Add graphics to `graphics/pokemon/`
5. Update `src/data/pokemon/species_info.h` includes

### Modifying Battle Mechanics
- Battle logic: `src/battle_*.c`
- Move effects: `src/battle_script_commands.c`
- Abilities: Look for `ABILITY_*` in `src/battle_util.c`
- Be cautious: battle system is complex and frequently updated upstream

### Debugging
- Enable debug mode: `#define DEBUG_OVERWORLD_MENU TRUE` in `include/config/debug.h`
- Debug menu: Hold R and press Start in overworld
- Battle debug: Available in battle with debug enabled

## Project-Specific Notes

This fork is developing a **card battle system** (Fluorescent & Phosphorescent):
- This will replace the traditional battle mechanics and UI with a system based on a simplified version of the Pokémon Trading Card Game
- Follow pokeemerald-expansion patterns for all custom content
- Look for ways to tie into existing systems and mechancics to make changes as small and compatible as possible
- If possible, keep old mechanics and definitions intact for compatibility with upstream changes
- Always write tests for new mechanics, moves, species, etc when relevant
