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

static const struct CardMoveData sCardEmber = {
    .damage = 30,
};
