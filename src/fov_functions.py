import tcod as libtcod


def initialize_fov(game_map):
    fov_map = libtcod.map_new(game_map.width, game_map.height)

    for y in range(game_map.height):
        for x in range(game_map.width):
            libtcod.map_set_properties(m=fov_map, x=x, y=y, isTrans=not game_map.tiles[x][y].block_sight,
                                       isWalk=not game_map.tiles[x][y].blocked)

    return fov_map


def recompute_fov(fov_map, x, y, radius, light_walls=True, algorithm=0):
    libtcod.map_compute_fov(m=fov_map, x=x, y=y, radius=radius, light_walls=light_walls, algo=algorithm)
