// Card Battle System - Extended Move Data
// This file contains extended move data for the card-based battle system.
// Moves listed here will use the new battle mechanics.
// Moves not listed will fall back to standard behavior.

// To add a move to the card system:
// 1. Define card data here
// 2. Add .card = &sYourMoveCard to the move in moves_info.h

// Example usage:
// static const struct CardMoveData sCardPound = {
//     .damage = 50,
// };

// Add your card move data definitions below this line:

// Grass moves
static const struct CardMoveData sCardVineWhip = {
    .damage = 40,
    .energyNeeded = 2,
    .grassEnergyNeeded = 1,
};

static const struct CardMoveData sCardRazorLeaf = {
    .damage = 60,
    .energyNeeded = 3,
    .grassEnergyNeeded = 1,
};

static const struct CardMoveData sCardMegaDrain = {
    .damage = 80,
    .energyNeeded = 4,
    .grassEnergyNeeded = 2,
};

// Fire moves
static const struct CardMoveData sCardEmber = {
    .damage = 30,
    .energyNeeded = 1,
    .fireEnergyNeeded = 1,
};

static const struct CardMoveData sCardFireClaws = {
    .damage = 60,
    .energyNeeded = 3,
    .fireEnergyNeeded = 1,
};

static const struct CardMoveData sCardFireSpin = {
    .damage = 150,
    .energyNeeded = 4,
    .fireEnergyNeeded = 2,
};

// Water moves
static const struct CardMoveData sCardWaterGun = {
    .damage = 20,
    .energyNeeded = 1,
    .waterEnergyNeeded = 1,
};

static const struct CardMoveData sCardWaveSplash = {
    .damage = 40,
    .energyNeeded = 2,
    .waterEnergyNeeded = 1,
};

static const struct CardMoveData sCardHydroPump = {
    .damage = 80,
    .energyNeeded = 3,
    .waterEnergyNeeded = 2,
};
