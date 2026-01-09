// Card Battle System - Extended Species Data
// This file contains extended species data for the card-based battle system.
// Species listed here will use the new battle mechanics.
// Species not listed will fall back to standard behavior.

// To add a species to the card system:
// 1. Define card data here
// 2. Add .card = &sCardYourSpecies to the species in species_info files

// Example usage:
// static const struct CardSpeciesData sCardPikachu = {
//     .weakness = TYPE_GROUND,
// };

// Add your card species data definitions below this line:

// Gen 1 Starters
static const struct CardSpeciesData sCardBulbasaur = {
    .weakness = TYPE_FIRE,
};

static const struct CardSpeciesData sCardIvysaur = {
    .weakness = TYPE_FIRE,
};

static const struct CardSpeciesData sCardVenusaur = {
    .weakness = TYPE_FIRE,
};

static const struct CardSpeciesData sCardCharmander = {
    .weakness = TYPE_WATER,
};

static const struct CardSpeciesData sCardCharmeleon = {
    .weakness = TYPE_WATER,
};

static const struct CardSpeciesData sCardCharizard = {
    .weakness = TYPE_WATER,
};

static const struct CardSpeciesData sCardSquirtle = {
    .weakness = TYPE_ELECTRIC,
};

static const struct CardSpeciesData sCardWartortle = {
    .weakness = TYPE_ELECTRIC,
};

static const struct CardSpeciesData sCardBlastoise = {
    .weakness = TYPE_ELECTRIC,
};
