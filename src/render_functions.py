from enum import IntEnum

import tcod as libtcod


class RenderOrder(IntEnum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3


def get_names_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.cx, mouse.cy)

    names = [entity.name for entity in entities
             if entity.x == x and entity.y == y and libtcod.map_is_in_fov(fov_map, entity.x, entity.y)]
    names = ', '.join(names)

    return names.capitalize()


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    libtcod.console_set_default_background(con=panel, col=back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_background(con=panel, col=bar_color)
    if bar_width > 0:
        libtcod.console_rect(con=panel, x=x, y=y, w=bar_width, h=1, clr=False, flag=libtcod.BKGND_SCREEN)

    libtcod.console_set_default_foreground(con=panel, col=libtcod.white)
    libtcod.console_print_ex(con=panel, x=int(x + total_width / 2), y=y, flag=libtcod.BKGND_NONE,
                             alignment=libtcod.CENTER, fmt='{}: {}/{}'.format(name, value, maximum))


def render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, screen_height,
               bar_width, panel_height, panel_y, mouse, colors):
    """
    Draw all entities in the list
    :param con: destination drawing console
    :param entities: list of Entity objects
    :param player: the player Entity object
    :param game_map: GameMap object
    :param fov_map: map of field of view
    :param fov_recompute: boolean
    :param screen_width: int width of screen
    :param screen_height: int height of screen
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

    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)
    
    # Print the game messages, one line at a time
    y = 1
    for message in message_log.messages:
        libtcod.console_set_default_foreground(panel, message.color)
        libtcod.console_print_ex(panel, message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
        y += 1
    
    render_bar(panel, 1, 1, bar_width, 'HP', player.fighter.hp, player.fighter.max_hp,
               libtcod.light_red, libtcod.darker_red)

    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT,
                             get_names_under_mouse(mouse, entities, fov_map))

    libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)
    

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
