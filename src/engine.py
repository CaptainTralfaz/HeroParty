import tcod as libtcod

from src.components.party import Party, PartyMember
from src.death_functions import kill_monster, kill_player
from src.entity import Entity, get_blocking_entities_at_location
from src.fov_functions import initialize_fov, recompute_fov
from src.game_messages import MessageLog, Message
from src.game_states import GameStates
from src.input_handlers import handle_keys
from src.map_objects.game_map import GameMap
from src.render_functions import render_all, clear_all, RenderOrder


def main():
    screen_width = 80
    screen_height = 50
    
    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height
    
    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1
    
    map_width = 80
    map_height = 43
    
    # Conway's Game Of Life variables
    # 3 6 5 6 3 - good choice
    # 3 6 5 7 3 - another good choice
    # 3 5 5 6 4 - larger, more open
    # 2 4 6 8 6 - very full, but lots of obstacles (Forest?)
    # 3 7 5 6 4 - small, windy, lots of caverns
    survive_min = 3
    survive_max = 7
    resurrect_min = 6
    resurrect_max = 6
    iterations = 4
    
    # zone variables
    zone_seed_min_distance = 10
    min_cavern_size = 15
    max_monsters_per_room = 3
    
    fov_radius = 8
    
    colors = {
        'dark_wall': libtcod.darker_gray,
        'dark_ground': libtcod.dark_gray,
        'light_wall': libtcod.sepia,
        'light_ground': libtcod.light_sepia
    }
    
    party_component = Party()
    member_1 = PartyMember(name="Bill", profession="Soldier", offensive_cd=4, defensive_cd=4,
                           attack_type={'melee': 1}, cost=5)
    member_2 = PartyMember(name="John", profession="Archer", offensive_cd=5, defensive_cd=5,
                           attack_type={'ranged': 4}, cost=4)
    member_3 = PartyMember(name="Sam", profession="Defender", offensive_cd=5, defensive_cd=3,
                           attack_type={'melee': 1}, cost=5)
    party_component.add_member(member_1)
    party_component.add_member(member_2)
    party_component.add_member(member_3)
    player = Entity(x=0, y=0, char='@', color=libtcod.white, name='Hero Party', blocks=True,
                    render_order=RenderOrder.ACTOR,
                    party=party_component)
    entities = [player]
    
    libtcod.console_set_custom_font(fontFile='images/arial10x10.png',
                                    flags=libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    
    libtcod.console_init_root(w=screen_width, h=screen_height, title='Hero Party', fullscreen=False)
    
    con = libtcod.console_new(w=screen_width, h=screen_height)
    panel = libtcod.console_new(w=screen_width, h=panel_height)
    
    game_map = GameMap(width=map_width, height=map_height)
    game_map.make_map(survive_min=survive_min, survive_max=survive_max, resurrect_min=resurrect_min,
                      resurrect_max=resurrect_max, iterations=iterations,
                      zone_seed_min_distance=zone_seed_min_distance,
                      min_cavern_size=min_cavern_size, player=player, entities=entities,
                      max_monsters_per_room=max_monsters_per_room)
    
    fov_recompute = True
    fov_map = initialize_fov(game_map=game_map)
    
    message_log = MessageLog(x=message_x, width=message_width, height=message_height)
    
    key = libtcod.Key()
    mouse = libtcod.Mouse()
    
    game_state = GameStates.PLAYER_TURN
    previous_member = None
    
    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(mask=libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, k=key, m=mouse)
        
        if fov_recompute:
            recompute_fov(fov_map=fov_map, x=player.x, y=player.y, radius=fov_radius)
        
        render_all(con=con, panel=panel, entities=entities, player=player, game_map=game_map, fov_map=fov_map,
                   fov_recompute=fov_recompute, message_log=message_log, screen_width=screen_width,
                   screen_height=screen_height, acting_member=previous_member,
                   bar_width=bar_width, panel_height=panel_height, panel_y=panel_y, mouse=mouse, colors=colors)
        
        libtcod.console_flush()
        
        clear_all(con=con, entities=entities)
        
        # --------- PLAYER TURN: GET INPUTS -------------
        action = handle_keys(key=key, game_state=game_state)
        
        move = action.get('move')
        exit_game = action.get('exit_game')
        fullscreen = action.get('fullscreen')
        auto = action.get('auto')
        selected_member = action.get('member')
        act_dir = action.get('act_dir')
        
        # --------- PLAYER TURN: PROCESS INPUTS -------------
        player_turn_results = []
        
        # AUTOMATIC -----------------------------------------
        if auto and GameStates.PLAYER_TURN:
            for entity in entities:
                if not entity.ai and not entity.blocks and entity.party.members \
                        and entity.x == player.x and entity.y == player.y:
                    player_turn_results.append({'add_member': entity})
                elif not entity.ai and not entity.blocks and entity.party.coins \
                        and entity.x == player.x and entity.y == player.y:
                    player_turn_results.append({'loot_coins': entity})
            else:  # Wait
                game_state = GameStates.ENEMY_TURN
        
        # MOVEMENT ------------------------------------------
        if move and game_state == GameStates.PLAYER_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy
            
            if not game_map.is_blocked(x=destination_x, y=destination_y) \
                    and not get_blocking_entities_at_location(entities=entities, x=destination_x, y=destination_y):
                player.move(dx=dx, dy=dy)
                fov_recompute = True
                game_state = GameStates.ENEMY_TURN
                
        # SELECTED MEMBER -----------------------------------
        if selected_member and selected_member <= len(player.party.members) and \
                player.party.members[selected_member - 1].cooldown < 1:
            if not previous_member:
                previous_member = selected_member
                game_state = GameStates.TARGETING
                
            elif previous_member == selected_member:
                previous_member = None
                game_state = GameStates.PLAYER_TURN
        
        if act_dir and previous_member:
            (x, y) = act_dir
            target_x = x + player.x
            target_y = y + player.y
            target = get_blocking_entities_at_location(entities=entities, x=target_x, y=target_y)
            if target:
                attack_results = player.party.members[previous_member - 1].attack(target=target)
                player_turn_results.extend(attack_results)
                previous_member = None
                game_state = GameStates.ENEMY_TURN
            else:
                player_turn_results.append({'message': Message("No Enemies in target zone")})
            
        if exit_game:
            return True
        
        if fullscreen:
            libtcod.console_set_fullscreen(fullscreen=not libtcod.console_is_fullscreen())
        
        # --------- PLAYER TURN: PROCESS RESULTS -------------
        for result in player_turn_results:
            rescued_members = result.get('add_member')
            message = result.get('message')
            dead_entity = result.get('dead')
            loot_coins = result.get('loot_coins')
            
            if rescued_members:
                for member in rescued_members.party.members:
                    msg, res = player.party.add_member(member)
                    message_log.add_message(msg)
                    if res:
                        entities.remove(rescued_members)
            
            if loot_coins:
                msg = player.party.add_coins(loot_coins.party.coins)
                message_log.add_message(msg)
                entities.remove(loot_coins)
            
            if message:
                message_log.add_message(message=message)
            
            if dead_entity:
                if dead_entity == player:
                    msg, game_state = kill_player(dead_entity)
                else:
                    msg = kill_monster(dead_entity)
                
                message_log.add_message(message=msg)
        
        # --------- ENEMY TURN: GET INPUT -------------
        if game_state == GameStates.ENEMY_TURN:
            entities_in_distance_order = sorted(entities, key=lambda z: z.distance_to(player))
            
            for entity in entities_in_distance_order:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(target=player, fov_map=fov_map, game_map=game_map,
                                                             entities=entities)
                    # --------- ENEMY TURN: PROCESS RESULTS -------------
                    for result in enemy_turn_results:
                        message = result.get('message')
                        dead_entity = result.get('dead')
                        
                        if message:
                            message_log.add_message(message=message)
                        
                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(player=dead_entity)
                            else:
                                message = kill_monster(entity=dead_entity)
                            
                            message_log.add_message(message=message)
                            
                            if game_state == GameStates.PLAYER_DEAD:
                                break
                    
                    if game_state == GameStates.PLAYER_DEAD:
                        break
            
            else:
                game_state = GameStates.PLAYER_TURN
                for entity in entities:
                    if entity.party:
                        entity.party.tick_all()


if __name__ == '__main__':
    main()
