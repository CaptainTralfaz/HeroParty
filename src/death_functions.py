import tcod as libtcod

from src.game_messages import Message
from src.game_states import GameStates
from src.render_functions import RenderOrder


def kill_player(player):
    player.char = '%'
    player.color = libtcod.dark_red
    
    return Message(text='Your party has been slain!', color=libtcod.red), GameStates.PLAYER_DEAD


def kill_monster(entity):
    death_message = Message(text='{} is dead!'.format(entity.name.capitalize()), color=libtcod.orange)
    
    entity.char = '%'
    entity.color = libtcod.dark_red
    entity.blocks = False
    entity.render_order = RenderOrder.CORPSE
    entity.ai = None
    entity.name = 'Remains of {}'.format(entity.name)
    
    return death_message
