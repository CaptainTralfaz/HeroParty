import tcod as libtcod


class BasicMonster:
    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            
            if monster.distance_to(target) >= 2:
                monster.move_astar(target=target, entities=entities, game_map=game_map)
            
            elif target.party.members and monster.party.random_member_no_cooldown():
                attack_results = monster.party.random_member_no_cooldown().attack(target=target)
                results.extend(attack_results)
        return results
