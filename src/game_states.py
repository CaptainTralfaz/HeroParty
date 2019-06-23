from enum import IntEnum


class GameStates(IntEnum):
    PLAYERS_TURN = 1
    ENEMY_TURN = 2
    PLAYER_DEAD = 3
