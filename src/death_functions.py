import tcod as libtcod

from src.game_states import GameStates
from src.render_functions import RenderOrder
from src.game_messages import Message


def kill_player(player):
    player.char = '%'
    player.color = libtcod.dark_red
    
    return Message('You died!', libtcod.red), GameStates.PLAYER_DEAD


def kill_monster(monster):
    death_message = Message('{} is dead!'.format(monster.name.capitalize()), libtcod.orange)
    
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.render_order = RenderOrder.CORPSE
    monster.fighter = None
    monster.ai = None
    monster.name = 'Remains of {}'.format(monster.name)
    
    return death_message
