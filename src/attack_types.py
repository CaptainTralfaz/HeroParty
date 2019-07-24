import tcod as libtcod

from src.game_messages import Message

# 2 = South
# 3 = West
# 0 = North
# 1 = East
directions = [(0, 1), (-1, 0), (0, -1), (1, 0)]


def get_line_tiles(distance):
    """
    create a set of tiles in a line extending from origin (to be rotated and translated later)
    :param distance: length of line
    :return: target tiles
    """
    tiles = []
    for y in range(1, distance + 1):
        tiles.append((0, y))
    return tiles


def get_cone_tiles(distance):
    """
    create a set of tiles in a triangle shape extending from origin (to be rotated and translated later)
    :param distance: height of triangle
    :return: target tiles
    """
    tiles = []
    for y in range(1, distance + 1):
        for x in range(1 - y, y):
            tiles.append((x, y))
    return tiles


def get_cross_tiles(distance):
    """
    create a cross of tiles a certain distance from origin (to be rotated and translated later)
    :param distance: distance of center of cross from origin
    :return: target tiles
    """
    tiles = [(0, distance)]
    for x, y in directions:
        tiles.append((x, y + distance))
    return tiles


def relational_tiles(origin, target_tiles):
    """
    Adjust tiles to origin point
    :param origin: x/y tuple of coordinates to translate to
    :param target_tiles: list of tile adjustments in attack zone in relation to (0, 0)
    :return: list of actual tile coordinates in attack zone
    """
    results = []
    (ox, oy) = origin
    for (x, y) in target_tiles:
        results.append((ox + x, oy + y))
    return results


def translational_tiles(direction, target_tiles):
    """
    rotate target coordinates in relation to direction
    :param direction:
    :param target_tiles:
    :return:
    """
    translated_targets = []
    if direction == (0, -1):  # UP
        for x, y in target_tiles:
            translated_targets.append((-x, -y))
    elif direction == (1, 0):  # RIGHT
        for x, y in target_tiles:
            translated_targets.append((y, -x))
    elif direction == (0, 1):  # DOWN
        for x, y in target_tiles:
            translated_targets.append((x, y))
    elif direction == (-1, 0):  # LEFT
        for x, y in target_tiles:
            translated_targets.append((-y, x))
    return translated_targets


def remove_blocked_target_tiles(game_map, target_tiles, fov_map):
    """
    removes blocked tiles, and tiles not in fov from attack zone
    :param game_map: GameMap object
    :param target_tiles: tiles available to attack
    :param fov_map: tiles that can be seen
    :return: list of attackable tiles
    """
    non_blocked = []
    for (x, y) in target_tiles:
        if not game_map.tiles[x][y].block_sight and libtcod.map_is_in_fov(m=fov_map, x=x, y=y):
            non_blocked.append((x, y))
    return non_blocked


def get_target_tiles(entity, member, game_map, fov_map, attack_dir=None):
    """
    collects all tiles available to target, or only a subset in one direction
    :param entity: party doing the attacking
    :param member: int member of group that is attacking
    :param game_map: GameMap object
    :param fov_map: list of visible tiles
    :param attack_dir: int tuple of coordinates corresponding to attack direction
    :return: list of attackable tiles
    """
    attack_type = entity.party.members[member].attack_type
    target_tiles = []
    if not attack_dir:
        attack_dir = directions
    for direction in attack_dir:
        if attack_type.get('line'):
            dir_tiles = get_line_tiles(attack_type['line'])
            target_tiles.extend(translational_tiles(direction, dir_tiles))
        elif attack_type.get('direct'):
            dir_tiles = get_line_tiles(attack_type['direct'])
            target_tiles.extend(translational_tiles(direction, dir_tiles))
        elif attack_type.get('cone'):
            dir_tiles = get_cone_tiles(attack_type['cone'])
            target_tiles.extend(translational_tiles(direction, dir_tiles))
    target_tiles = relational_tiles((entity.x, entity.y), target_tiles)
    target_tiles = remove_blocked_target_tiles(game_map, target_tiles, fov_map)
    return target_tiles


# class ActionType:
#     def __init__(self, use_function=None, attack_type=None, targeting=False, targeting_message=None, sustained=0,
#                  **kwargs):
#         self.use_function = use_function
#         self.type = attack_type
#         self.targeting = targeting
#         self.targeting_message = targeting_message
#         self.sustained = sustained
#         self.function_kwargs = kwargs
#
#
# def heal(*args, **kwargs):
#     entity = args[0]
#     amount = kwargs.get('amount')
#
#     results = []
#
#     # check party for injuries
#     members_on_cooldown = [member for member in entity.party.members if member.cooldown > 0]
#
#     if not members_on_cooldown:
#         results.append({'no_action': True, 'message': Message('Nobody is injured', libtcod.yellow)})
#     else:
#         results.append({'message': Message("The Party's wounds start to fade!", libtcod.green)})
#         entity.party.tick_all(amount)
#
#     return results
