import tcod as libtcod

from src.game_messages import Message


class ActionType:
    def __init__(self, use_function=None, targeting=False, targeting_message=None, sustained=0, **kwargs):
        self.use_function = use_function
        self.targeting = targeting
        self.targeting_message = targeting_message
        self.sustained = sustained
        self.function_kwargs = kwargs

    
def heal(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get('amount')
    
    results = []
    
    # check party for injuries
    members_on_cooldown = [member for member in entity.party.members if member.cooldown > 0]
    
    if not members_on_cooldown:
        results.append({'no_action': True, 'message': Message('Nobody is injured', libtcod.yellow)})
    else:
        results.append({'message': Message("The Party's wounds start to fade!", libtcod.green)})
        entity.party.tick_all(amount)

    return results


def melee(*args, **kwargs):
    entity = args[0]
    member_number = kwargs.get('member')
    entities = kwargs.get('entities')
    # distance = kwargs.get('distance')
    direction = kwargs.get('direction')
    
    results = []
    
    (dx, dy) = direction
    target_tile = (entity.x + dx, entity.y + dy)
    target = None
    
    for entity in entities:
        if entity.ai and (entity.x, entity.y) == target_tile:
            target = entity
    if target:
        attack_results = entity.party.member[member_number].attack(target=target)
        results.extend(attack_results)
    
    return results
