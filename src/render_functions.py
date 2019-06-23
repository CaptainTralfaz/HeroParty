import tcod as libtcod


def render_all(con, entities, game_map, fov_map, fov_recompute, screen_width, screen_height, colors):
    """
    Draw all entities in the list
    :param con: destination drawing console
    :param entities: list of entity objects
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
                        # libtcod.console_set_char(con=con, x=x, y=y, c='.')
                        libtcod.console_set_char_background(con=con, x=x, y=y, col=colors.get('light_ground'),
                                                            flag=libtcod.BKGND_SET)
                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored:
                    if wall:
                        libtcod.console_set_char_background(con=con, x=x, y=y, col=colors.get('dark_wall'),
                                                            flag=libtcod.BKGND_SET)
                    else:
                        libtcod.console_set_char_background(con=con, x=x, y=y, col=colors.get('dark_ground'),
                                                            flag=libtcod.BKGND_SET)

    for entity in entities:
        draw_entity(con=con, entity=entity, fov_map=fov_map)

    libtcod.console_blit(src=con, x=0, y=0, w=screen_width, h=screen_height, dst=0, xdst=0, ydst=0)


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