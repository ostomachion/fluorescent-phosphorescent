#include "global.h"
#include "battle.h"
#include "battle_util.h"
#include "battle_controllers.h"
#include "battle_message.h"
#include "battle_scripts.h"
#include "pokemon.h"
#include "move.h"
#include "constants/battle_move_effects.h"

// Card Battle System
// This system provides completely separate battle mechanics for moves with card data.
// Card moves bypass all standard battle mechanics (accuracy, animations, type effectiveness, etc.)
// and execute with their own simplified logic.

void HandleCardMove(void)
{
    const struct CardMoveData *cardData = gMovesInfo[gCurrentMove].card;
    
    if (cardData == NULL)
        return; // Should never happen, but safety check
    
    s32 damage = cardData->damage;
    
    // Check for card weakness mechanic
    // If target has card species data with a weakness, check if it matches attacker's type
    u16 targetSpecies = gBattleMons[gBattlerTarget].species;
    const struct CardSpeciesData *targetCardData = gSpeciesInfo[targetSpecies].card;
    
    if (targetCardData != NULL)
    {
        // Get attacker's types
        u16 attackerSpecies = gBattleMons[gBattlerAttacker].species;
        u8 attackerType1 = gSpeciesInfo[attackerSpecies].types[0];
        u8 attackerType2 = gSpeciesInfo[attackerSpecies].types[1];
        
        // Check if target is weak to either of attacker's types
        // TYPE_NONE means no weakness, so skip it
        if (targetCardData->weakness != TYPE_NONE 
            && (targetCardData->weakness == attackerType1 || targetCardData->weakness == attackerType2))
        {
            damage += 20; // Add weakness damage bonus
            // Set super effective flag for sound/message
            gBattleStruct->moveResultFlags[gBattlerTarget] |= MOVE_RESULT_SUPER_EFFECTIVE;
        }
    }
    
    // Store damage - the battle script will handle actually applying it to HP
    gBattleStruct->moveDamage[gBattlerTarget] = damage;
    
    // Set the battle script for card move execution
    // The script handles: animation, damage sound, HP updates, faint check, and moveendall
    // moveendall handles all post-move effects including updating last move tracking
    gBattlescriptCurrInstr = BattleScript_CardMoveHit;
}
