from random import randint, choice

import tcod as libtcod

from src.components.ai import BasicMonster
from src.components.party import PartyMember, Party
from src.entity import Entity
from src.map_objects.caverns import create_caverns
from src.map_objects.tile import Tile
from src.render_functions import RenderOrder


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
        
        # place the player in the first zone
        player.x, player.y = choice(zones[0])
        
        # place other stuff in other zones
        for zone in zones[1:]:
            self.place_entities(zone=zone, entities=entities, max_monsters_per_room=max_monsters_per_room)
        
        # not currently using corridors for anything interesting :/
    
    def place_entities(self, zone, entities, max_monsters_per_room):
        # Get a random number of monsters
        number_of_monsters = randint(0, max_monsters_per_room)
        for i in range(number_of_monsters):
            # Choose a random location in the room
            (x, y) = choice(zone)
            
            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                value = randint(0, 100)
                if value <= 90:
                    party_component = Party(coins=randint(1, 5))
                    member_1 = PartyMember(name="Brute", profession="Kobold", offensive_cd=5, defensive_cd=4,
                                           attack_type={'melee': 1}, cost=0)
                    party_component.add_member(member_1)
                    if randint(0, 1):
                        member_2 = PartyMember(name="Rogue", profession="Kobold", offensive_cd=4, defensive_cd=5,
                                               attack_type={'melee': 1}, cost=0)
                        party_component.add_member(member_2)
                    # if randint(0, 1):
                    #     member_3 = PartyMember(name="Slinger", profession="Kobold", offensive_cd=5, defensive_cd=5,
                    #                            attack_type={'ranged': 3}, cost=0)
                    #     party_component.add_member(member_3)
                    ai_component = BasicMonster()
                    monster = Entity(x=x, y=y, char='k', color=libtcod.light_green, name='Kobold Pack',
                                     blocks=True, render_order=RenderOrder.ACTOR, party=party_component,
                                     ai=ai_component)
                else:
                    hero_component = PartyMember(name="Ted", profession="Spearman", offensive_cd=5, defensive_cd=5,
                                                 attack_type={'melee': 2}, cost=5)
                    party_component = Party(coins=0)
                    party_component.add_member(hero_component)
                    monster = Entity(x=x, y=y, char='@', color=libtcod.dark_orange, name='Hero', blocks=False,
                                     render_order=RenderOrder.ITEM, party=party_component)
                
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
