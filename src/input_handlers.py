import tcod as libtcod
from src.game_states import GameStates


def handle_keys(key, game_state):
    if game_state == GameStates.PLAYER_TURN:
        return handle_keys_player_turn(key=key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_keys_player_dead(key=key)
    elif game_state == GameStates.TARGETING:
        return handle_keys_targeting(key=key)


def handle_mouse(mouse):
    (x, y) = (mouse.cx, mouse.cy)
    
    if mouse.lbutton_pressed:
        print(x, y)
        return {'left_click': (x, y)}
    elif mouse.rbutton_pressed:
        print(x, y)
        return {'right_click': (x, y)}

    return {}


def handle_keys_targeting(key):
    if key.vk == libtcod.KEY_UP:
        return {'act_dir': (0, -1)}
    elif key.vk == libtcod.KEY_DOWN:
        return {'act_dir': (0, 1)}
    elif key.vk == libtcod.KEY_LEFT:
        return {'act_dir': (-1, 0)}
    elif key.vk == libtcod.KEY_RIGHT:
        return {'act_dir': (1, 0)}
    elif key.vk == libtcod.KEY_1:
        return {'member': 1}
    elif key.vk == libtcod.KEY_2:
        return {'member': 2}
    elif key.vk == libtcod.KEY_3:
        return {'member': 3}
    elif key.vk == libtcod.KEY_4:
        return {'member': 4}
    elif key.vk == libtcod.KEY_5:
        return {'member': 5}
    elif key.vk == libtcod.KEY_6:
        return {'member': 6}
    
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}
    
    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit the game
        return {'exit': True}
    
    # No key was pressed
    return {}


def handle_keys_player_turn(key):
    # Movement keys
    if key.vk == libtcod.KEY_UP:
        return {'move': (0, -1)}
    elif key.vk == libtcod.KEY_DOWN:
        return {'move': (0, 1)}
    elif key.vk == libtcod.KEY_LEFT:
        return {'move': (-1, 0)}
    elif key.vk == libtcod.KEY_RIGHT:
        return {'move': (1, 0)}
    elif key.vk == libtcod.KEY_SPACE:
        return {'auto': True}
    elif key.vk == libtcod.KEY_1:
        return {'member': 1}
    elif key.vk == libtcod.KEY_2:
        return {'member': 2}
    elif key.vk == libtcod.KEY_3:
        return {'member': 3}
    elif key.vk == libtcod.KEY_4:
        return {'member': 4}
    elif key.vk == libtcod.KEY_5:
        return {'member': 5}
    elif key.vk == libtcod.KEY_6:
        return {'member': 6}

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}
    
    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit the game
        return {'exit_game': True}
    
    # No key was pressed
    return {}


def handle_keys_player_dead(key):
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}
    
    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit the game
        return {'exit_game': True}
    
    # No key was pressed
    return {}
