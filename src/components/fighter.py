class Fighter:
    def __init__(self, hp, defense, power):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
    
    def take_damage(self, amount):
        results = []
        self.hp -= amount
        if self.hp <= 0:
            results.append({'dead': self.owner})
        return results
    
    def attack(self, target):
        results = []
        damage = self.power - target.fighter.defense
        
        if damage > 0:
            results.append({'message': '{} attacks {} for {} hit points.'.format(self.owner.name.capitalize(),
                                                                                 target.name, damage)})
            results.extend(target.fighter.take_damage(amount=damage))
        else:
            results.append({'message': '{} attacks {} but does no damage.'.format(
                self.owner.name.capitalize(), target.name)})
        
        return results
