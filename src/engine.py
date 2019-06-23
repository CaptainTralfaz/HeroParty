import tcod as libtcod

from src.components.fighter import Fighter
from src.death_functions import kill_monster, kill_player
from src.entity import Entity, get_blocking_entities_at_location
from src.fov_functions import initialize_fov, recompute_fov
from src.game_states import GameStates
from src.input_handlers import handle_keys
from src.map_objects.game_map import GameMap
from src.render_functions import render_all, clear_all, RenderOrder


def main():
    """
    Testing GitHub integration
    :return: None
    """
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 45
    
    room_max_size = 10
    room_min_size = 6
    max_rooms = 30
    max_monsters_per_room = 3
    
    fov_radius = 8
    
    colors = {
        'dark_wall': libtcod.Color(0, 0, 100),
        'dark_ground': libtcod.Color(50, 50, 150),
        'light_wall': libtcod.Color(130, 110, 50),
        'light_ground': libtcod.Color(200, 180, 50)
    }
    
    fighter_component = Fighter(hp=30, defense=2, power=5)
    player = Entity(x=0, y=0, char='@', color=libtcod.white, name='Player', blocks=True, render_order=RenderOrder.ACTOR,
                    fighter=fighter_component)
    entities = [player]
    
    libtcod.console_set_custom_font(fontFile='images/arial10x10.png',
                                    flags=libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    
    libtcod.console_init_root(w=screen_width, h=screen_height, title='Hero Party', fullscreen=False)
    
    con = libtcod.console_new(w=screen_width, h=screen_height)
    
    game_map = GameMap(width=map_width, height=map_height)
    game_map.make_map(max_rooms=max_rooms, room_min_size=room_min_size, room_max_size=room_max_size,
                      map_width=map_width, map_height=map_height, player=player, entities=entities,
                      max_monsters_per_room=max_monsters_per_room)
    
    fov_recompute = True
    fov_map = initialize_fov(game_map=game_map)
    
    key = libtcod.Key()
    mouse = libtcod.Mouse()
    
    game_state = GameStates.PLAYERS_TURN
    
    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(mask=libtcod.EVENT_KEY_PRESS, k=key, m=mouse)
        
        if fov_recompute:
            recompute_fov(fov_map=fov_map, x=player.x, y=player.y, radius=fov_radius)
        
        render_all(con=con, entities=entities, player=player, game_map=game_map, fov_map=fov_map,
                   fov_recompute=fov_recompute, screen_width=screen_width, screen_height=screen_height, colors=colors)
        
        libtcod.console_flush()
        
        clear_all(con=con, entities=entities)
        
        action = handle_keys(key=key)
        
        move = action.get('move')
        exit_game = action.get('exit_game')
        fullscreen = action.get('fullscreen')
        wait = action.get('wait')
        
        player_turn_results = []
        
        if wait and GameStates.PLAYERS_TURN:
            game_state = GameStates.ENEMY_TURN
        
        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy
            
            if not game_map.is_blocked(x=destination_x, y=destination_y):
                target = get_blocking_entities_at_location(entities=entities, x=destination_x, y=destination_y)
                
                if target:
                    attack_results = player.fighter.attack(target=target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(dx=dx, dy=dy)
                    fov_recompute = True
                
                game_state = GameStates.ENEMY_TURN
        
        if exit_game:
            return True
        
        if fullscreen:
            libtcod.console_set_fullscreen(fullscreen=not libtcod.console_is_fullscreen())
        
        for result in player_turn_results:
            message = result.get('message')
            dead_entity = result.get('dead')
            
            if message:
                print(message)
            
            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)
                
                print(message)
        
        if game_state == GameStates.ENEMY_TURN:
            entities_in_distance_order = sorted(entities, key=lambda z: z.distance_to(player))
            
            for entity in entities_in_distance_order:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(target=player, fov_map=fov_map, game_map=game_map,
                                                             entities=entities)
                    for result in enemy_turn_results:
                        message = result.get('message')
                        dead_entity = result.get('dead')
                        
                        if message:
                            print(message)
                        
                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(player=dead_entity)
                            else:
                                message = kill_monster(dead_entity)
                            
                            print(message)
                            
                            if game_state == GameStates.PLAYER_DEAD:
                                break
                    
                    if game_state == GameStates.PLAYER_DEAD:
                        break
            
            else:
                game_state = GameStates.PLAYERS_TURN


if __name__ == '__main__':
    main()
