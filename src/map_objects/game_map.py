from src.map_objects.tile import Tile
from src.map_objects.rectangle import Rect
from random import randint, choice
from src.entity import Entity
import tcod as libtcod
from src.components.ai import BasicMonster
from src.render_functions import RenderOrder
from src.components.party import PartyMember, Party
from src.map_objects.caverns import create_caverns


class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
    
    def initialize_tiles(self):
        return [[Tile(True) for y in range(self.height)] for x in range(self.width)]
    
    def make_map(self, survive_min, survive_max, resurrect_min, resurrect_max, iterations,
                 zone_seed_min_distance, min_cavern_size, player, entities, max_monsters_per_room):
        life_map, zones, corridors = create_caverns(map_width=self.width, map_height=self.height,
                                                    survive_min=survive_min, survive_max=survive_max,
                                                    resurrect_min=resurrect_min, resurrect_max=resurrect_max,
                                                    iterations=iterations,
                                                    zone_seed_min_distance=zone_seed_min_distance,
                                                    min_cavern_size=min_cavern_size)
        # convert LifeMap to GameMap
        for x in range(self.width):
            for y in range(self.height):
                if not life_map.alive[x][y]:
                    self.tiles[x][y].blocked = False
                    self.tiles[x][y].block_sight = False
                
        # place the player
        player.x, player.y = choice(choice(zones))

        for zone in zones:
            self.place_entities(zone=zone, entities=entities, max_monsters_per_room=max_monsters_per_room)
        
        # not currently using corridors for anything interesting :/

    def place_entities(self, zone, entities, max_monsters_per_room):
        # Get a random number of monsters
        number_of_monsters = randint(0, max_monsters_per_room)
        
        for i in range(number_of_monsters):
            # Choose a random location in the room
            (x, y) = choice(zone)
            
            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                if randint(0, 100) <= 100:
                    party_component = Party(coins=randint(50, 100))
                    member_1 = PartyMember(name="Brute", profession="Kobold", offensive_cd=5, defensive_cd=4,
                                           attack_type=1, cost=0)
                    # member_2 = PartyMember(name="Rogue", profession="Kobold", offensive_cd=4, defensive_cd=5,
                    #                        attack_type=1, cost=0)
                    party_component.add_member(member_1)
                    # party_component.add_member(member_2)
                    ai_component = BasicMonster()
                    monster = Entity(x=x, y=y, char='k', color=libtcod.desaturated_green, name='Kobold Pack',
                                     blocks=True, render_order=RenderOrder.ACTOR, party=party_component,
                                     ai=ai_component)
                # else:
                #     fighter_component = Fighter(hp=16, defense=1, power=4)
                #     ai_component = BasicMonster()
                #     monster = Entity(x=x, y=y, char='T', color=libtcod.darker_green, name='Troll', blocks=True,
                #                      render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
                
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
