from queue import Queue
from random import randint, choice


life_directions = {(-1, -1), (-1, 0), (-1, 1), (0, 1),
                   (1, 1), (1, 0), (1, -1), (0, -1)}

ortho_directions = {(1, 0), (0, 1), (-1, 0), (0, -1)}


class LifeMap:
    def __init__(self, map_width, map_height):
        """
        Creates a new map (list of lists) and initializes it to all random, except for a filled border
        :param map_width: width of map
        :param map_height: height of map
        """
        self.width = map_width
        self.height = map_height
        self.alive = [[True for y in range(self.height)] for x in range(self.width)]
    
    def make_random(self):
        for x in range(1, self.width - 1):
            for y in range(1, self.height - 1):
                if randint(0, 1):
                    self.alive[x][y] = False


def carve_tile_sets(grid, tile_sets):
    """
    Sets each point in a list of lists of tile coordinates as False
    :param grid: current 2d boolean array
    :param tile_sets: list of list of tuples representing unconnected caverns
    :return: modified grid
    """
    for tile_set in tile_sets:
        grid = carve_tiles(grid=grid, tiles=tile_set)
    return grid


def carve_tiles(grid, tiles):
    """
    Sets each point in a list of lists of tile coordinates as False
    :param grid: current 2d boolean array
    :param tiles: list of tuples representing unconnected caverns
    :return: modified grid
    """
    for (x, y) in tiles:
        grid.alive[x][y] = False
    return grid


def connect_caverns_closest(grid, caverns, min_cavern_size):
    """
    Connect caverns using closest tiles rather than random tiles
     - strategy: sort the caverns smallest to largest
     - start with the smallest cavern
     - flood fill neighboring WALLS until a FLOOR neighbor is detected that is NOT part of current cavern
     - THAT floor neighbor is the closest point
     - check point against original cavern tile points for distance set of smallest distances
     - choose one of those closest points to connect to
     - repeat for next largest cavern (re-sort caverns) until there is only one cavern
    :param grid: current LifeMap Object
    :param caverns: list of list of tuples representing unconnected caverns
    :param min_cavern_size: int minimum number of tiles in a cavern
    :return: list of tuple int x y coordinates (corridors)
    """
    all_corridors = []
    while len(caverns) > 1:
        caverns.sort(key=len)
        closest = explore_walls_iterative_ortho(grid, caverns[0])
        target = find_nearest_point_in_cavern(closest, caverns[0])
        corridors = connect_caverns_random_walk(closest, target)
        all_corridors.extend(corridors)
        carve_tiles(grid=grid, tiles=corridors)
        
        # get new list of caverns
        grid, caverns = fill_small_caverns(grid=grid, min_cavern_size=min_cavern_size)
    
    return all_corridors


def connect_caverns_random_walk(closest, target):
    """
    Chooses a random coordinate in each separate cavern set,
    and then connects those points in a random-walk algorithm,
    setting to false as it progresses
    :param closest: tuple representing starting point of walk
    :param target: tuple representing ending point of walk
    :return: list of tuple int x y coordinates (corridors)
    """
    corridors = []
    (x1, y1) = closest
    (x2, y2) = target
    while (x1, y1) != (x2, y2):
        if x1 == x2:  # move y
            if y1 < y2:
                y1 += 1
            else:
                y1 -= 1
        elif y1 == y2:  # move x
            if x1 < x2:
                x1 += 1
            else:
                x1 -= 1
        else:
            if randint(0, 1):  # randomly pick x or y
                if y1 < y2:
                    y1 += 1
                else:
                    y1 -= 1
            else:
                if x1 < x2:
                    x1 += 1
                else:
                    x1 -= 1
        corridors.append((x1, y1))
    corridors.remove(target)
    return corridors


def find_nearest_point_in_cavern(start, cavern):
    """
    compare orthogonal distances between a point and a set of another points to find closest
    :param start: tile coordinates
    :param cavern: list of tiles in a cavern
    :return: target coordinate
    """
    target = cavern[0]
    (x1, y1) = start
    (x2, y2) = target
    cavern.remove(target)
    shortest_dist = distance_to(x1=x1, y1=y1, x2=x2, y2=y2)
    for (x2, y2) in cavern:
        distance = distance_to(x1=x1, y1=y1, x2=x2, y2=y2)
        if distance < shortest_dist:
            shortest_dist = distance
            target = (x2, y2)
    return target


def cleanup(grid, min_cavern_size):
    """
    Create a map without the small caverns, with all valid caverns connected
    :param grid: current 2d boolean array
    :param min_cavern_size: int minimum size of unconnected
    :return: modified copy of grid, list of lists of tuple int x y coordinates
    """
    new_grid = LifeMap(map_width=grid.width, map_height=grid.height)
    # copy grid
    for x in range(grid.width):
        for y in range(grid.height):
            if not grid.alive[x][y]:
                new_grid.alive[x][y] = False
    
    # get a map without the small caverns, with all valid caverns connected
    new_grid, valid_caverns = fill_small_caverns(grid=new_grid, min_cavern_size=min_cavern_size)
    
    return new_grid, valid_caverns


def fill_small_caverns(grid, min_cavern_size):
    """
    Finds the coordinates of all enclosed caverns, sends only valid caverns to be carved
    :param grid: current LifeMap object
    :param min_cavern_size: int minimum cavern size to keep
    :return: current lifeMap object, list of lists of tuple int x y locations
    """
    cavern_tiles = []  # holds sets of all coordinates in largest caverns found so far
    explored = []
    new_grid = LifeMap(map_width=grid.width, map_height=grid.height)
    for x in range(new_grid.width):
        for y in range(new_grid.height):
            if (x, y) not in cavern_tiles and (x, y) not in explored and not grid.alive[x][y]:
                # get all tiles in this cave system
                new_cave_tiles = explore_cavern_iterative_ortho(grid, x, y)
                # compare size of new cave tiles to current tile
                explored.extend(new_cave_tiles)
                if len(new_cave_tiles) >= min_cavern_size:
                    cavern_tiles.append(new_cave_tiles)
    new_map = carve_tile_sets(grid=new_grid, tile_sets=cavern_tiles)
    return new_map, cavern_tiles


def get_starting_seeds(caverns, min_cavern_size, zone_seed_min_distance):
    """
    Create starting zone seeds with the following strategy:
    1 determine maximum number of possible seeds
    2 pick a random tile in a cave as a seed
    3 remove all other tiles within a certain distance as seed candidates
    4 repeat 2 and 3 until there are no valid candidates
    :param caverns: list of lists of cavern tiles
    :param min_cavern_size: helps determine maximum number of seeds
    :param zone_seed_min_distance:
    :return: list of seed coordinates
    """
    seeds = []
    for cavern in caverns:
        valid_seeds = cavern
        cavern_seed_count = len(cavern) // min_cavern_size
        
        while valid_seeds and len(valid_seeds) >= cavern_seed_count:
            seed = choice(valid_seeds)
            seeds.append(seed)
            valid_seeds.remove(seed)
            valid_seeds = remove_closest_candidates(seed=seed, candidates=valid_seeds,
                                                    zone_seed_min_distance=zone_seed_min_distance)
    return seeds


def get_neighbor_count(grid, x, y, state):
    """
    Convenience function: Returns a count of tuple x y coordinates matching a desired state - diagonal version
    :param grid: LifeMap object
    :param x: x coordinate
    :param y: y coordinate
    :param state: desired boolean state to match
    :return: list of tuple x y coordinates
    """
    return len(get_neighbors_list(grid=grid, x=x, y=y, state=state))


def get_neighbor_count_ortho(grid, x, y, state):
    """
    Convenience function: Returns a count of tuple x y coordinates matching a desired state - orthogonal version
    :param grid: LifeMap object
    :param x: x coordinate
    :param y: y coordinate
    :param state: desired boolean state to match
    :return: list of tuple x y coordinates
    """
    return len(get_neighbors_list_ortho(grid=grid, x=x, y=y, state=state))


def get_neighbors_list(grid, x, y, state):
    """
    Returns a list of tuple x y coordinates matching a desired state - diagonal version
    :param grid: LifeMap object
    :param x: x coordinate
    :param y: y coordinate
    :param state: desired boolean state to match
    :return: list of tuple x y coordinates
    """
    neighbors = []
    for direction in life_directions:
        dx, dy = direction
        if grid.alive[dx + x][dy + y] == state:
            neighbors.append((dx + x, dy + y))
    return neighbors


def get_neighbors_list_ortho(grid, x, y, state):
    """
    Returns a list of tuple x y coordinates matching a desired state - orthogonal version
    :param grid: LifeMap object
    :param x: x coordinate
    :param y: y coordinate
    :param state: desired boolean state to match
    :return: list of tuple x y coordinates
    """
    neighbors = []
    for direction in ortho_directions:
        (dx, dy) = direction
        if grid.alive[dx + x][dy + y] == state:
            neighbors.append((dx + x, dy + y))
    return neighbors


def explore_cavern_iterative(grid, x, y):
    """
    Iteratively explores a cavern, returns a list of all coordinates in that cavern - orthogonal version
    :param grid: LifeMap object
    :param x: x coordinate
    :param y: y coordinate
    :return: list of tuple x y coordinates
    """
    frontier = Queue()
    frontier.put((x, y))
    visited = [(x, y)]
    
    while not frontier.empty():
        current = frontier.get()
        x, y = current
        for neighbor in get_neighbors_list(grid, x, y, state=False):
            if neighbor not in visited:
                frontier.put(neighbor)
                visited.append(neighbor)
    return visited


def explore_cavern_iterative_ortho(grid, x, y):
    """
    Iteratively explores a cavern, returns a list of all coordinates in that cavern - orthogonal version
    :param grid: LifeMap object
    :param x: x coordinate
    :param y: y coordinate
    :return: list of tuple x y coordinates
    """
    frontier = Queue()
    frontier.put((x, y))
    visited = [(x, y)]
    
    while not frontier.empty():
        current = frontier.get()
        x, y = current
        for neighbor in get_neighbors_list_ortho(grid, x, y, state=False):
            if neighbor not in visited:
                frontier.put(neighbor)
                visited.append(neighbor)
    return visited


def explore_walls_iterative_ortho(grid, tile_set):
    """
    Iteratively explores walls from a set of points,
     - returns a list of all coordinates in that cavern - orthogonal version
    :param grid: LifeMap object
    :param tile_set: list of tuple int x y coordinates
    :return: closest "live" coordinates of next cave
    """
    frontier = Queue()
    visited = []
    closest = None
    
    for (x, y) in tile_set:
        visited.append((x, y))
        if get_neighbors_list_ortho(grid, x, y, state=True):
            frontier.put((x, y))
    while not frontier.empty() and not closest:
        current = frontier.get()
        x, y = current
        neighbors = []
        for (dx, dy) in ortho_directions:
            if (x + dx) in range(grid.width) and (y + dy) in range(grid.height):
                neighbors.append((x + dx, y + dy))
        for neighbor in neighbors:
            (x, y) = neighbor
            if (x, y) not in visited:
                if grid.alive[x][y]:
                    frontier.put(neighbor)
                    visited.append(neighbor)
                else:
                    closest = (x, y)
                    break
    return closest


def cycle(grid, survive_min, survive_max, resurrect_min, resurrect_max):
    """
    Heart of the Conway's Game Of Life algorithm for our purposes
    (credit to https://gridbugs.org/cellular-automata-cave-generation/)
    :param grid: list of lists of booleans denoting map
    :param survive_min: minimum number of neighbors needed to keep state
    :param survive_max: maximum number of neighbors allowed to keep state
    :param resurrect_min: minimum number of neighbors needed to change state
    :param resurrect_max: maximum number of neighbors allowed to change state
    :return: current lifeMap object after iteration
    """
    next_grid = LifeMap(map_width=grid.width, map_height=grid.height)
    for x in range(1, grid.width - 1):
        for y in range(1, grid.height - 1):
            neighbor_count = get_neighbor_count(grid=grid, x=x, y=y, state=True)
            if grid.alive[x][y]:
                if survive_min <= neighbor_count <= survive_max:
                    next_grid.alive[x][y] = True
                else:
                    next_grid.alive[x][y] = False
            else:
                if resurrect_min <= neighbor_count <= resurrect_max:
                    next_grid.alive[x][y] = True
                else:
                    next_grid.alive[x][y] = False
    return next_grid


def make_zones(grid, starting_seeds):
    """
    Creates zones to be used for monster / treasure placement (instead of rooms)
    :param grid: LifeMap object
    :param starting_seeds: list of tuple int x y coordinates (one from each "cavern")
    :return: list of lists of tuple int x y coordinates
    """
    # copy map
    taken_grid = LifeMap(grid.width, grid.height)
    for x in range(grid.width):
        for y in range(grid.height):
            if not grid.alive[x][y] or (x, y) in starting_seeds:
                taken_grid.alive[x][y] = False
    
    # convert lifeMap object into a list of valid coordinates
    grid_list = []
    for x in range(grid.width):
        for y in range(grid.height):
            if not grid.alive[x][y]:
                grid_list.append((x, y))
    
    # change list of seed tuples into a list of lists
    zones = []
    for seed in starting_seeds:
        zones.append([seed])
    
    # grow seeds into zones, until there are no more valid coordinates to choose from
    while grid_list:
        zones, grid_list = grow_zones(zones=zones, grid_list=grid_list, grid=grid)
    
    return zones


def grow_zones(zones, grid_list, grid):
    """
    Iterate through zones tile by tile, appending each tile's valid neighbors to it's zone
    :param zones: list of lists of tuple int x y coordinates
    :param grid_list: list of available tiles
    :param grid: LifeMap object (array of array of booleans)
    :return: new list of zones, list of valid coordinates
    """
    zone_list = []
    for zone in zones:
        new_zone = []
        for (x, y) in zone:
            new_zone.append((x, y))
            neighbors = get_neighbors_list_ortho(grid=grid, x=x, y=y, state=False)
            for neighbor in neighbors:
                if neighbor in grid_list:
                    new_zone.append(neighbor)
                    grid_list.remove(neighbor)
        zone_list.append(new_zone)
    return zone_list, grid_list


def remove_closest_candidates(seed, candidates, zone_seed_min_distance):
    """
    Removes all candidates with orthogonal distance smaller than the given min distance
    :param seed: tuple x y int coordinates
    :param candidates: list of tuple x y int coordinates that can be removed
    :param zone_seed_min_distance: minimum distance coordinates must be from seed
    :return: list of tuple x y int valid candidates
    """
    good_list = []
    (x1, y1) = seed
    for candidate in candidates:
        (x2, y2) = candidate
        good_candidate = True
        if distance_to(x1, y1, x2, y2) < zone_seed_min_distance:
            good_candidate = False
        if good_candidate:
            good_list.append(candidate)
    return good_list


def furthest_candidate_from_all_seeds(seeds, candidates):
    """
    Returns the candidate coordinate that is the farthest in distance from all seeds
    :param seeds: list of int x y coordinate tuples
    :param candidates: list of int x y coordinate tuples
    :return: tuple x y int coordinates
    """
    furthest_dist = 0
    furthest_candidate = (None, None)
    for (x1, y1) in candidates:
        current_dist = 0
        for (x2, y2) in seeds:
            current_dist += distance_to(x1, y1, x2, y2)
            if current_dist > furthest_dist:
                furthest_dist = current_dist
                furthest_candidate = (x1, y1)
    return furthest_candidate


def distance_to(x1, y1, x2, y2):
    """
    Sum the difference between two points
    :param x1: point 1 x coord
    :param y1: point 1 y coord
    :param x2: point 2 x coord
    :param y2: point 2 y coord
    :return: int orthogonal distance
    """
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    return dx + dy


def create_caverns(map_width, map_height, survive_min, survive_max, resurrect_min, resurrect_max, iterations,
                   zone_seed_min_distance, min_cavern_size):

    # create random LifeMap object
    life_map = LifeMap(map_width=map_width, map_height=map_height)
    life_map.make_random()
    
    # cycle LifeMap object a desired number of times
    for i in range(iterations):
        life_map = cycle(grid=life_map, survive_min=survive_min, survive_max=survive_max,
                         resurrect_min=resurrect_min, resurrect_max=resurrect_max)
    
    # clean up LifeMap object, connecting areas that are large enough
    life_map, caverns = cleanup(grid=life_map, min_cavern_size=min_cavern_size)
    
    starting_seeds = get_starting_seeds(caverns=caverns, min_cavern_size=min_cavern_size,
                                        zone_seed_min_distance=zone_seed_min_distance)
    
    # create zones (rooms) in map for monster/treasure placement
    zones = make_zones(grid=life_map, starting_seeds=starting_seeds)
    
    # connect zones
    corridors = connect_caverns_closest(grid=life_map, caverns=caverns, min_cavern_size=min_cavern_size)
    carve_tiles(grid=life_map, tiles=corridors)
    
    return life_map, zones, corridors
