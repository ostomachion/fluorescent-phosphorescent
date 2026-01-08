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
    
    // Store damage - the battle script will handle actually applying it to HP
    gBattleStruct->moveDamage[gBattlerTarget] = damage;
    
    // Set the battle script for card move execution
    // The script handles: animation, damage sound, HP updates, faint check, and moveendall
    // moveendall handles all post-move effects including updating last move tracking
    gBattlescriptCurrInstr = BattleScript_CardMoveHit;
}
