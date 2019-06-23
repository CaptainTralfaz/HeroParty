from src.map_objects.tile import Tile
from src.map_objects.rectangle import Rect
from random import randint
from src.entity import Entity
import tcod as libtcod


class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
    
    def initialize_tiles(self):
        return [[Tile(True) for y in range(self.height)] for x in range(self.width)]
    
    def create_room(self, room):
        """
        go through the tiles in the rectangle and make them passable
        :param room: Rect object
        :return: None
        """
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False
    
    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
    
    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
    
    def create_random_walk_tunnel(self, x1, x2, y1, y2):
        x = x1
        y = y1
        while (x, y) != (x2, y2):
            if x == x2:
                # move y
                if y < y2:
                    y += 1
                else:
                    y -= 1
            elif y == y2:
                # move x
                if x < x2:
                    x += 1
                else:
                    x -= 1
            else:
                # randomly pick x or y
                if randint(0, 1):
                    if y < y2:
                        y += 1
                    else:
                        y -= 1
                else:
                    if x < x2:
                        x += 1
                    else:
                        x -= 1
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
    
    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player,
                 entities, max_monsters_per_room):
        """
        Generates a basic dungeon
        :param max_rooms: int maximum number of rooms
        :param room_min_size: int smallest length or width a room can be
        :param room_max_size: int largest length or width a room can be
        :param map_width: int width of map
        :param map_height: int height of map
        :param player: object player entity
        :param entities: list of Entity Objects
        :param max_monsters_per_room: int number of possible Entity Objects in room
        :return: None
        """
        rooms = []
        num_rooms = 0
        
        for r in range(max_rooms):
            # random width and height
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            # random position without going out of the boundaries of the map
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)
            
            # "Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)
            
            # run through the other rooms and see if they intersect with this one
            for other_room in rooms:
                if new_room.intersect(other=other_room):
                    break
            else:
                # this means there are no intersections, so this room is valid
                
                # "paint" it to the map's tiles
                self.create_room(room=new_room)
                
                # random coordinates of new room, will be useful later
                new_x, new_y = new_room.random()
                
                if num_rooms == 0:
                    # this is the first room, where the player starts at
                    player.x = new_x
                    player.y = new_y
                else:
                    # all rooms after the first:
                    # connect it to the previous room with a tunnel
                    
                    # random coordinates of previous room
                    (prev_x, prev_y) = rooms[num_rooms - 1].random()
                    
                    # flip a coin (random number that is either 0 or 1)
                    self.create_random_walk_tunnel(x1=prev_x, x2=new_x, y1=prev_y, y2=new_y)
                    # if randint(0, 1) == 1:
                    #     # first move horizontally, then vertically
                    #     self.create_h_tunnel(x1=prev_x, x2=new_x, y=prev_y)
                    #     self.create_v_tunnel(y1=prev_y, y2=new_y, x=new_x)
                    # else:
                    #     # first move vertically, then horizontally
                    #     self.create_v_tunnel(y1=prev_y, y2=new_y, x=prev_x)
                    #     self.create_h_tunnel(x1=prev_x, x2=new_x, y=new_y)
                
                self.place_entities(room=new_room, entities=entities, max_monsters_per_room=max_monsters_per_room)
                
                # finally, append the new room to the list
                rooms.append(new_room)
                num_rooms += 1
    
    def place_entities(self, room, entities, max_monsters_per_room):
        # Get a random number of monsters
        number_of_monsters = randint(0, max_monsters_per_room)
        
        for i in range(number_of_monsters):
            # Choose a random location in the room
            x, y = room.random()
            
            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                if randint(0, 100) < 80:
                    monster = Entity(x, y, 'o', libtcod.desaturated_green, 'Orc', blocks=True)
                else:
                    monster = Entity(x, y, 'T', libtcod.darker_green, 'Troll', blocks=True)
                
                entities.append(monster)
    
    def is_blocked(self, x, y):
        """
        Tests whether a location blocks movement
        :param x: x location on map
        :param y: y location on map
        :return: boolean True if blocked, else False
        """
        if self.tiles[x][y].blocked:
            return True
        return False
