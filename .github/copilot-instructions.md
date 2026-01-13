# GitHub Copilot Instructions for pokeemerald-expansion

## Project Overview
This project is based on **pokeemerald-expansion** from RHH (Rom Hacking Hideout), a comprehensive toolkit for creating Pokémon GBA ROM hacks built on top of pret's pokeemerald decompilation.

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

### Quick Build
```bash
make -j$(nproc)  # Linux/WSL
```

### Clean Build (when things break)
```bash
make clean && make -j16
```

### Build Target Info
- Default target: `pokeemerald.gba` (modern ROM)
- Debug build: `make debug` (includes debug symbols)
- The ROM will be ~26MB and use ~92% of EWRAM

### Common Build Issues
- **Missing types (u32, u8, etc.)**: Header include order issue - check that `#include "global.h"` is first
- **Struct incomplete type**: Missing struct definition, check includes
- **Link errors**: Usually means a function signature changed - rebuild from clean

## Development Guidelines

### Code Style
- Follow the existing code style in pokeemerald-expansion
- Use proper type definitions: `u32`, `u16`, `u8`, `s32`, etc. (not `int`)
- Use `enum` types where defined (e.g., `enum Move`, `enum Ability`, `enum Type`)
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

## Resources

### Documentation
- Main docs: https://rh-hideout.github.io/pokeemerald-expansion/
- Features list: [FEATURES.md](FEATURES.md)
- Changelog: [docs/CHANGELOG.md](docs/CHANGELOG.md)

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
