#define LEVEL_UP_MOVE(lvl, moveLearned) {.move = moveLearned, .level = lvl}
#define LEVEL_UP_END {.move = LEVEL_UP_MOVE_END, .level = 0}

#if P_FAMILY_BULBASAUR
static const struct LevelUpMove sBulbasaurCardA1N1LevelUpLearnset[] = {
    LEVEL_UP_MOVE(1, MOVE_VINE_WHIP),
    LEVEL_UP_END
};
#endif //P_FAMILY_BULBASAUR

#if P_FAMILY_CHARMANDER
static const struct LevelUpMove sCharmanderCardA1N33LevelUpLearnset[] = {
    LEVEL_UP_MOVE(1, MOVE_EMBER),
    LEVEL_UP_END
};
#endif //P_FAMILY_CHARMANDER

#if P_FAMILY_SQUIRTLE
static const struct LevelUpMove sSquirtleCardA1N53LevelUpLearnset[] = {
    LEVEL_UP_MOVE(1, MOVE_WATER_GUN),
    LEVEL_UP_END
};
#endif //P_FAMILY_SQUIRTLE
