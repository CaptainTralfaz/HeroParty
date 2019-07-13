from enum import IntEnum


class GameStates(IntEnum):
    PLAYER_TURN = 1
    ENEMY_TURN = 2
    PLAYER_DEAD = 3
    TARGETING = 4
