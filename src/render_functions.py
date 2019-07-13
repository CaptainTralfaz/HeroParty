from enum import IntEnum

import tcod as libtcod


class RenderOrder(IntEnum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3


def get_names_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.cx, mouse.cy)
    
    names = [entity.name for entity in entities
             if entity.x == x and entity.y == y and libtcod.map_is_in_fov(m=fov_map, x=entity.x, y=entity.y)]
    names = ', '.join(names)
    
    return names


def get_party_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.cx, mouse.cy)
    for entity in entities:
        if entity.x == x and entity.y == y and libtcod.map_is_in_fov(m=fov_map, x=entity.x, y=entity.y) and entity.ai:
            return entity
    return None


def render_bar(panel, x, y, total_width, name, value, bar_color, back_color):
    bar_width = total_width  # int(float(value) / maximum * total_width)
    
    libtcod.console_set_default_background(con=panel, col=back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)
    
    libtcod.console_set_default_background(con=panel, col=bar_color)
    if bar_width > 0:
        libtcod.console_rect(con=panel, x=x, y=y, w=bar_width, h=1, clr=False, flag=libtcod.BKGND_SCREEN)
    
    libtcod.console_set_default_foreground(con=panel, col=libtcod.white)
    libtcod.console_print_ex(con=panel, x=1, y=y, flag=libtcod.BKGND_NONE,
                             alignment=libtcod.LEFT, fmt='[{}] {}'.format(y, name))
    libtcod.console_print_ex(con=panel, x=total_width, y=y, flag=libtcod.BKGND_NONE,
                             alignment=libtcod.RIGHT, fmt='CD:{}'.format(value))


def render_member(panel, x, y, member, width, text_color):
    libtcod.console_set_default_foreground(con=panel, col=text_color)
    libtcod.console_print_ex(con=panel, x=x, y=y, flag=libtcod.BKGND_NONE, alignment=libtcod.LEFT,
                             fmt='{}:{} {}'.format(y, member.profession, member.name))
    libtcod.console_print_ex(con=panel, x=width, y=y, flag=libtcod.BKGND_NONE, alignment=libtcod.RIGHT,
                             fmt='({})'.format(member.cooldown))


def render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, screen_height,
               bar_width, panel_height, panel_y, mouse, colors):
    """
    Draw all entities in the list
    :param con: destination drawing console
    :param panel: drawing surface for messages, etc.
    :param entities: list of Entity objects
    :param player: the player Entity object
    :param game_map: GameMap object
    :param fov_map: map of field of view
    :param fov_recompute: boolean
    :param message_log: MessageLog object containing list of messages
    :param screen_width: int width of screen
    :param screen_height: int height of screen
    :param bar_width: int width of bar for panel
    :param panel_height: int height of panel
    :param panel_y: int location of panel
    :param mouse: tuple mouse location
    :param colors: dict of color tuples
    :return: None
    """
    if fov_recompute:
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = libtcod.map_is_in_fov(m=fov_map, x=x, y=y)
                wall = game_map.tiles[x][y].block_sight
                
                if visible:
                    if wall:
                        libtcod.console_set_char_foreground(con=con, x=x, y=y, col=colors.get('light_ground'))
                        libtcod.console_set_char(con=con, x=x, y=y, c='-')
                        libtcod.console_set_char_background(con=con, x=x, y=y, col=colors.get('light_wall'),
                                                            flag=libtcod.BKGND_SET)
                    else:
                        libtcod.console_set_char_foreground(con=con, x=x, y=y, col=colors.get('light_wall'))
                        libtcod.console_set_char(con=con, x=x, y=y, c='.')
                        libtcod.console_set_char_background(con=con, x=x, y=y, col=colors.get('light_ground'),
                                                            flag=libtcod.BKGND_SET)
                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored:
                    if wall:
                        libtcod.console_set_char(con=con, x=x, y=y, c=' ')
                        libtcod.console_set_char_background(con=con, x=x, y=y, col=colors.get('dark_wall'),
                                                            flag=libtcod.BKGND_SET)
                    else:
                        libtcod.console_set_char(con=con, x=x, y=y, c=' ')
                        libtcod.console_set_char_background(con=con, x=x, y=y, col=colors.get('dark_ground'),
                                                            flag=libtcod.BKGND_SET)
    
    entities_in_render_order = sorted(entities, key=lambda z: z.render_order.value)
    
    for entity in entities_in_render_order:
        draw_entity(con=con, entity=entity, fov_map=fov_map)
    
    # noinspection PyTypeChecker
    libtcod.console_blit(src=con, x=0, y=0, w=screen_width, h=screen_height, dst=0, xdst=0, ydst=0)
    
    libtcod.console_set_default_background(con=panel, col=libtcod.darker_gray)
    libtcod.console_clear(con=panel)
    
    # Print the game messages, one line at a time
    y = 1
    for message in message_log.messages:
        # libtcod.console_set_key_color(panel, libtcod.gray)
        libtcod.console_set_default_foreground(con=panel, col=message.color)
        libtcod.console_print_ex(con=panel, x=message_log.x, y=y, flag=libtcod.BKGND_NONE, alignment=libtcod.LEFT,
                                 fmt=message.text)
        y += 1
    
    # get entities under mouse
    text2 = None
    text = get_names_under_mouse(mouse=mouse, entities=entities, fov_map=fov_map)
    if not text:
        text = player.name
        text2 = 'Gold: {}'.format(player.party.coins)
    libtcod.console_set_default_foreground(con=panel, col=libtcod.white)
    libtcod.console_print_ex(con=panel, x=1, y=0, flag=libtcod.BKGND_NONE, alignment=libtcod.LEFT, fmt=text)
    if text2:
        libtcod.console_print_ex(con=panel, x=bar_width, y=0, flag=libtcod.BKGND_NONE, alignment=libtcod.RIGHT,
                                 fmt=text2)
    
    target = get_party_under_mouse(mouse=mouse, entities=entities, fov_map=fov_map)
    if not target:
        target = player
    
    y = 1
    x = 1
    for member in target.party.members:
        if member.cooldown > 0:
            text_color = libtcod.red
        else:
            text_color = libtcod.white
        render_member(panel, x, y, member, width=bar_width, text_color=text_color)
        y += 1
    
    # y = 1
    # for member in player.party.members:
    #     if member.cooldown > 0:
    #         render_bar(panel=panel, x=1, y=y, total_width=bar_width, name=member.name, value=member.cooldown,
    #                    bar_color=libtcod.darker_red, back_color=libtcod.darker_red)
    #     else:
    #         render_bar(panel=panel, x=1, y=y, total_width=bar_width, name=member.name, value=member.cooldown,
    #                    bar_color=libtcod.darker_gray, back_color=libtcod.darker_gray)
    #     y += 1
    
    # noinspection PyTypeChecker
    libtcod.console_blit(src=panel, x=0, y=0, w=screen_width, h=panel_height, dst=0, xdst=0, ydst=panel_y)


def clear_all(con, entities):
    """
    Clear all entities in the list
    :param con: destination drawing console
    :param entities: list of entity objects
    :return: None
    """
    for entity in entities:
        clear_entity(con=con, entity=entity)


def draw_entity(con, entity, fov_map):
    """
    Draws a single entity to console
    :param con: destination drawing console
    :param entity: entity object
    :param fov_map: map of field of view
    :return: None
    """
    if libtcod.map_is_in_fov(m=fov_map, x=entity.x, y=entity.y):
        libtcod.console_set_default_foreground(con=con, col=entity.color)
        libtcod.console_put_char(con=con, x=entity.x, y=entity.y, c=entity.char, flag=libtcod.BKGND_NONE)


def clear_entity(con, entity):
    """
    Draws a blank over a single entity on the console
    :param con: destination drawing console
    :param entity: entity object
    :return: None
    """
    libtcod.console_put_char(con=con, x=entity.x, y=entity.y, c=' ', flag=libtcod.BKGND_NONE)
