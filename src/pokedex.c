#include "global.h"
#include "battle_script_commands.h"
#include "event_data.h"
#include "malloc.h"
#include "menu.h"
#include "palette.h"
#include "pokedex.h"
#include "pokedex_plus_hgss.h"
#include "string_util.h"
#include "strings.h"
#include "trainer_pokemon_sprites.h"

#define MAX_MONS_ON_SCREEN 4

#define POKEBALL_ROTATION_TOP    64
#define POKEBALL_ROTATION_BOTTOM (POKEBALL_ROTATION_TOP - 16)

static EWRAM_DATA u16 sLastSelectedPokemon = 0;
static EWRAM_DATA u8 sPokeBallRotation = 0;

// This is written to, but never read.
COMMON_DATA u8 gUnusedPokedexU8 = 0;
COMMON_DATA void (*gPokedexVBlankCB)(void) = NULL;

static u32 GetMeasurementTextPositions(u32 textElement);
static void PrintUnknownMonMeasurements(void);
static u8* GetUnknownMonHeightString(void);
static u8* GetUnknownMonWeightString(void);
static u8* ReplaceDecimalSeparator(const u8* originalString);
static void PrintOwnedMonMeasurements(u16 species);
static void PrintOwnedMonHeight(u16 species);
static void PrintOwnedMonWeight(u16 species);
static u8* ConvertMonHeightToImperialString(u32 height);
static u8* ConvertMonHeightToMetricString(u32 height);
static u8* ConvertMonWeightToImperialString(u32 weight);
static u8* ConvertMonWeightToMetricString(u32 weight);
static u8* ConvertMeasurementToMetricString(u32 num, u32* index);

// const rom data
#include "data/pokemon/pokedex_orders.h"

void CB2_OpenPokedex(void)
{
    CB2_OpenPokedexPlusHGSS();
}



void ResetPokedex(void)
{
    u16 i;

    sLastSelectedPokemon = 0;
    sPokeBallRotation = POKEBALL_ROTATION_TOP;
    gUnusedPokedexU8 = 0;
    gSaveBlock2Ptr->pokedex.mode = DEX_MODE_NATIONAL;
    gSaveBlock2Ptr->pokedex.order = 0;
    gSaveBlock2Ptr->pokedex.nationalMagic = 0xDA;
    gSaveBlock2Ptr->pokedex.unknown2 = 0;
    gSaveBlock2Ptr->pokedex.unownPersonality = 0;
    gSaveBlock2Ptr->pokedex.spindaPersonality = 0;
    gSaveBlock2Ptr->pokedex.unknown3 = 0;
    EnableNationalPokedex();
    for (i = 0; i < NUM_DEX_FLAG_BYTES; i++)
    {
        gSaveBlock1Ptr->dexCaught[i] = 0;
        gSaveBlock1Ptr->dexSeen[i] = 0;
    }
}

void ResetPokedexScrollPositions(void)
{
    sLastSelectedPokemon = 0;
    sPokeBallRotation = POKEBALL_ROTATION_TOP;
}

#define sIsDownArrow data[1]

static void PrintInfoScreenText(const u8 *str, u8 left, u8 top)
{
    u8 color[3];
    color[0] = TEXT_COLOR_TRANSPARENT;
    color[1] = TEXT_DYNAMIC_COLOR_6;
    color[2] = TEXT_COLOR_LIGHT_GRAY;

    AddTextPrinterParameterized4(0, FONT_NORMAL, left, top, 0, 0, color, TEXT_SKIP_DRAW, str);
}

#define tState         data[0]
#define tSpecies        data[1]
#define tPalTimer      data[2]
#define tMonSpriteId   data[3]
#define tIsShiny       data[13]
#define tPersonalityLo 14
#define tPersonalityHi 15

u8 DisplayCaughtMonDexPage(u16 species, bool32 isShiny, u32 personality)
{
    u8 taskId = CreateTask(Task_DisplayCaughtMonDexPageHGSS, 0);

    gTasks[taskId].tState = 0;
    gTasks[taskId].tSpecies = species;
    gTasks[taskId].tIsShiny = isShiny;
    gTasks[taskId].data[tPersonalityLo] = personality;
    gTasks[taskId].data[tPersonalityHi] = personality >> 16;
    return taskId;
}

u32 Pokedex_CreateCaughtMonSprite(u32 species, s32 x, s32 y)
{
    u32 spriteId;

    SetMultiuseSpriteTemplateToPokemon(species, GetCatchingBattler());
    spriteId = CreateSprite(&gMultiuseSpriteTemplate, x, y, 0);
    gSprites[spriteId].oam.priority = 0;
    gSprites[spriteId].callback = SpriteCallbackDummy;
    return spriteId;
}

#undef tState
#undef tSpecies
#undef tPalTimer
#undef tMonSpriteId
#undef tOtIdLo
#undef tOtIdHi
#undef tPersonalityLo
#undef tPersonalityHi


void PrintMonMeasurements(u16 species, u32 owned)
{
    u32 x = GetMeasurementTextPositions(DEX_HEADER_X);
    u32 yTop = GetMeasurementTextPositions(DEX_Y_TOP);
    u32 yBottom = GetMeasurementTextPositions(DEX_Y_BOTTOM);

    PrintInfoScreenText(gText_HTHeight, x, yTop);
    PrintInfoScreenText(gText_WTWeight, x, yBottom);

    if (owned)
        PrintOwnedMonMeasurements(species);
    else
        PrintUnknownMonMeasurements();
}

static u32 GetMeasurementTextPositions(u32 textElement)
{
    switch(textElement)
    {
        case DEX_HEADER_X:
            return (DEX_HEADER_X + DEX_HGSS_HEADER_X_PADDING);
        case DEX_Y_TOP:
            return (DEX_Y_TOP + DEX_HGSS_Y_TOP_PADDING);
        case DEX_Y_BOTTOM:
            return (DEX_Y_BOTTOM + DEX_HGSS_Y_BOTTOM_PADDING);
        default:
        case DEX_MEASUREMENT_X:
            return (DEX_MEASUREMENT_X + DEX_HGSS_MEASUREMENT_X_PADDING);
    }
}

static void PrintUnknownMonMeasurements(void)
{
    u8* heightString = GetUnknownMonHeightString();
    u8* weightString = GetUnknownMonWeightString();

    u32 x = GetMeasurementTextPositions(DEX_MEASUREMENT_X);
    u32 yTop = GetMeasurementTextPositions(DEX_Y_TOP);
    u32 yBottom = GetMeasurementTextPositions(DEX_Y_BOTTOM);

    PrintInfoScreenText(heightString, x, yTop);
    PrintInfoScreenText(weightString, x, yBottom);

    Free(heightString);
    Free(weightString);
}

static u8* GetUnknownMonHeightString(void)
{
    if (UNITS == UNITS_IMPERIAL)
        return ReplaceDecimalSeparator(gText_UnkHeight);
    else
        return ReplaceDecimalSeparator(gText_UnkHeightMetric);
}

static u8* GetUnknownMonWeightString(void)
{
    if (UNITS == UNITS_IMPERIAL)
        return ReplaceDecimalSeparator(gText_UnkWeight);
    else
        return ReplaceDecimalSeparator(gText_UnkWeightMetric);
}



static u8* ReplaceDecimalSeparator(const u8* originalString)
{
    bool32 replaced = FALSE;
    u32 length = StringLength(originalString), i;
    u8* modifiedString = Alloc(WEIGHT_HEIGHT_STR_MEM);

    for (i = 0; i < length; i++)
    {
        if ((originalString[i] != CHAR_PERIOD) || replaced)
        {
            modifiedString[i] = originalString[i];
            continue;
        }

        modifiedString[i] = CHAR_DEC_SEPARATOR;
        replaced = TRUE;
    }
    modifiedString[length] = EOS;
    return modifiedString;
}

static void PrintOwnedMonMeasurements(u16 species)
{
    PrintOwnedMonHeight(species);
    PrintOwnedMonWeight(species);
}

static void PrintOwnedMonHeight(u16 species)
{
    u32 height = GetSpeciesHeight(species);
    u8* heightString;

    u32 x = GetMeasurementTextPositions(DEX_MEASUREMENT_X);
    u32 yTop = GetMeasurementTextPositions(DEX_Y_TOP);

    heightString = ConvertMonHeightToString(height);

    PrintInfoScreenText(heightString, x, yTop);
    Free(heightString);
}

u8* ConvertMonHeightToString(u32 height)
{
    if (UNITS == UNITS_IMPERIAL)
        return ConvertMonHeightToImperialString(height);
    else
        return ConvertMonHeightToMetricString(height);
}

static void PrintOwnedMonWeight(u16 species)
{
    u32 weight = GetSpeciesWeight(species);
    u8* weightString;
    u32 x = GetMeasurementTextPositions(DEX_MEASUREMENT_X);
    u32 yBottom = GetMeasurementTextPositions(DEX_Y_BOTTOM);

    weightString = ConvertMonWeightToString(weight);

    PrintInfoScreenText(weightString, x, yBottom);
    Free(weightString);
}

u8* ConvertMonWeightToString(u32 weight)
{
    if (UNITS == UNITS_IMPERIAL)
        return ConvertMonWeightToImperialString(weight);
    else
        return ConvertMonWeightToMetricString(weight);
}

static u8* ConvertMonHeightToImperialString(u32 height)
{
    u8* heightString = Alloc(WEIGHT_HEIGHT_STR_MEM);
    u32 inches, feet, index = 0;

    inches = (height * 10000) / CM_PER_INCH_FACTOR;
    if (inches % 10 >= 5)
        inches += 10;
    feet = inches / INCHES_IN_FOOT_FACTOR;
    inches = (inches - (feet * INCHES_IN_FOOT_FACTOR)) / 10;

    heightString[index++] = EXT_CTRL_CODE_BEGIN;
    heightString[index++] = EXT_CTRL_CODE_CLEAR_TO;
    if (feet / 10 == 0)
    {
        heightString[index++] = INCHES_IN_ONE_AND_HALF_FOOT;
        heightString[index++] = feet + CHAR_0;
    }
    else
    {
        heightString[index++] = INCHES_IN_FOOT;
        heightString[index++] = feet / 10 + CHAR_0;
        heightString[index++] = (feet % 10) + CHAR_0;
    }
    heightString[index++] = CHAR_SGL_QUOTE_RIGHT;
    heightString[index++] = (inches / 10) + CHAR_0;
    heightString[index++] = (inches % 10) + CHAR_0;
    heightString[index++] = CHAR_DBL_QUOTE_RIGHT;
    heightString[index++] = EOS;

    return heightString;
}

static u8* ConvertMonHeightToMetricString(u32 height)
{
    u32 index = 0;
    u8* heightString = ConvertMeasurementToMetricString(height, &index);

    heightString[index++] = CHAR_m;
    heightString[index++] = EOS;
    return heightString;
}

static u8* ConvertMonWeightToImperialString(u32 weight)
{
    u8* weightString = Alloc(WEIGHT_HEIGHT_STR_MEM);
    bool32 output = FALSE;
    u32 index = 0, lbs = (weight * 100000) / DECAGRAMS_IN_POUND;

    if (lbs % 10u >= 5)
        lbs += 10;

    if ((weightString[index] = (lbs / 100000) + CHAR_0) == CHAR_0 && !output)
    {
        weightString[index++] = CHAR_SPACER;
    }
    else
    {
        output = TRUE;
        index++;
    }

    lbs %= 100000;
    if ((weightString[index] = (lbs / 10000) + CHAR_0) == CHAR_0 && !output)
    {
        weightString[index++] = CHAR_SPACER;
    }
    else
    {
        output = TRUE;
        index++;
    }

    lbs %= 10000;
    if ((weightString[index] = (lbs / 1000) + CHAR_0) == CHAR_0 && !output)
    {
        weightString[index++] = CHAR_SPACER;
    }
    else
    {
        output = TRUE;
        index++;
    }

    lbs %= 1000;
    weightString[index++] = (lbs / 100) + CHAR_0;
    lbs %= 100;
    weightString[index++] = CHAR_DEC_SEPARATOR;
    weightString[index++] = (lbs / 10) + CHAR_0;
    weightString[index++] = CHAR_SPACE;
    weightString[index++] = CHAR_l;
    weightString[index++] = CHAR_b;
    weightString[index++] = CHAR_s;
    weightString[index++] = CHAR_PERIOD;
    weightString[index++] = EOS;

    return weightString;
}

static u8* ConvertMonWeightToMetricString(u32 weight)
{
    u32 index = 0;
    u8* weightString = ConvertMeasurementToMetricString(weight, &index);

    weightString[index++] = CHAR_k;
    weightString[index++] = CHAR_g;
    weightString[index++] = CHAR_PERIOD;
    weightString[index++] = EOS;
    return weightString;
}

static u8* ConvertMeasurementToMetricString(u32 num, u32* index)
{
    u8* string = Alloc(WEIGHT_HEIGHT_STR_MEM);
    bool32 outputted = FALSE;
    u32 result;

    result = num / 1000;
    if (result == 0)
    {
        string[(*index)++] = CHAR_SPACER;
        outputted = FALSE;
    }
    else
    {
        string[(*index)++] = CHAR_0 + result;
        outputted = TRUE;
    }

    result = (num % 1000) / 100;
    if (result == 0 && !outputted)
    {
        string[(*index)++] = CHAR_SPACER;
        outputted = FALSE;
    }
    else
    {
        string[(*index)++] = CHAR_0 + result;
        outputted = TRUE;
    }

    string[(*index)++] = CHAR_0 + ((num % 1000) % 100) / 10;
    string[(*index)++] = CHAR_DEC_SEPARATOR;
    string[(*index)++] = CHAR_0 + ((num % 1000) % 100) % 10;
    string[(*index)++] = CHAR_SPACE;

    return string;
}

s8 GetSetPokedexFlag(enum NationalDexOrder nationalDexNo, u8 caseID)
{
    u32 index, bit, mask;
    s8 retVal = 0;

    nationalDexNo--;
    index = nationalDexNo / 8;
    bit = nationalDexNo % 8;
    mask = 1 << bit;

    switch (caseID)
    {
    case FLAG_GET_SEEN:
        retVal = ((gSaveBlock1Ptr->dexSeen[index] & mask) != 0);
        break;
    case FLAG_GET_CAUGHT:
         retVal = ((gSaveBlock1Ptr->dexCaught[index] & mask) != 0);
        break;
    case FLAG_SET_SEEN:
        gSaveBlock1Ptr->dexSeen[index] |= mask;
        break;
    case FLAG_SET_CAUGHT:
        gSaveBlock1Ptr->dexCaught[index] |= mask;
        break;
    }

    return retVal;
}

u16 GetNationalPokedexCount(u8 caseID)
{
    u16 count = 0;
    u16 i;

    for (i = 0; i < NATIONAL_DEX_COUNT; i++)
    {
        switch (caseID)
        {
        case FLAG_GET_SEEN:
            if (GetSetPokedexFlag(i + 1, FLAG_GET_SEEN))
                count++;
            break;
        case FLAG_GET_CAUGHT:
            if (GetSetPokedexFlag(i + 1, FLAG_GET_CAUGHT))
                count++;
            break;
        }
    }
    return count;
}

u16 GetHoennPokedexCount(u8 caseID)
{
    return GetNationalPokedexCount(caseID);
}

bool16 HasAllHoennMons(void)
{
    return HasAllMons();
}

bool16 HasAllMons(void)
{
    u32 i, j;

    for (i = 1; i < NATIONAL_DEX_COUNT + 1; i++)
    {
        j = NationalPokedexNumToSpecies(i);
        if (!(gSpeciesInfo[j].isMythical && !gSpeciesInfo[j].dexForceRequired) && !GetSetPokedexFlag(j, FLAG_GET_CAUGHT))
            return FALSE;
    }

    return TRUE;
}

// The footprints are drawn on WIN_FOOTPRINT, which uses BG palette 15 (loaded with graphics/text_window/message_box.gbapal)
// The footprint pixels are stored as 1BPP, and set to the below color index in this palette when converted to 4BPP.
#define FOOTPRINT_COLOR_IDX  2

#define NUM_FOOTPRINT_TILES  4

void DrawFootprint(u8 windowId, u16 species)
{
    u8 ALIGNED(4) footprint4bpp[TILE_SIZE_4BPP * NUM_FOOTPRINT_TILES];
    const u8 *footprintGfx = NULL;
    u32 i, j, tileIdx = 0;

#if P_FOOTPRINTS
    footprintGfx = gSpeciesInfo[SanitizeSpeciesId(species)].footprint;
#else
    return;
#endif

    if (footprintGfx != NULL)
    {
        for (i = 0; i < TILE_SIZE_1BPP * NUM_FOOTPRINT_TILES; i++)
        {
            u8 footprint1bpp = footprintGfx[i];

            // Convert the 8 pixels in the above 1BPP byte to 4BPP.
            // Each iteration creates one 4BPP byte (2 pixels),
            // so we need 4 iterations to do all 8 pixels.
            for (j = 0; j < 4; j++)
            {
                u8 tile = 0;
                if (footprint1bpp & (1 << (2 * j)))
                    tile |= FOOTPRINT_COLOR_IDX; // Set pixel
                if (footprint1bpp & (2 << (2 * j)))
                    tile |= FOOTPRINT_COLOR_IDX << 4; // Set pixel
                footprint4bpp[tileIdx] = tile;
                tileIdx++;
            }
        }
    }
    else
    {
        CpuFastFill(0, footprint4bpp, sizeof(footprint4bpp));
    }
    CopyToWindowPixelBuffer(windowId, footprint4bpp, sizeof(footprint4bpp), 0);
}


// Unown and Spinda use the personality of the first seen individual of that species
// All others use personality 0
static u32 GetPokedexMonPersonality(u16 species)
{
    if (species == SPECIES_UNOWN || species == SPECIES_SPINDA)
    {
        if (species == SPECIES_UNOWN)
            return gSaveBlock2Ptr->pokedex.unownPersonality;
        else
            return gSaveBlock2Ptr->pokedex.spindaPersonality;
    }
    else
    {
        return 0xFF; //Changed from 0 to make it so the Pokédex shows the default mon pics instead of the female versions.
    }
}

u16 CreateMonSpriteFromNationalDexNumber(enum NationalDexOrder nationalNum, s16 x, s16 y, u16 paletteSlot)
{
    nationalNum = NationalPokedexNumToSpecies(nationalNum);
    return CreateMonPicSprite(nationalNum, FALSE, GetPokedexMonPersonality(nationalNum), TRUE, x, y, paletteSlot, TAG_NONE);
}

#undef sIsDownArrow
