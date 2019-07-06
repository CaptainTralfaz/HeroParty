from random import choice

import tcod as libtcod

from src.game_messages import Message


class Party:
    def __init__(self, coins=100):
        """
        Class holder for a list of PartyMember objects, and how much coin the party is carrying
        :param coins: number of collected coins party currently has
        """
        self.members = []
        self.coins = coins
    
    def add_member(self, party_member):
        """
        Append a PartyMember to the list
        :param party_member: PartyMember object to add to the party list
        :return: results and message
        """
        if len(self.members) < 6:
            self.members.append(party_member)
            message = Message('{} {} added to party'.format(party_member.profession, party_member.name),
                              color=libtcod.lighter_blue)
            results = True
        else:
            message = Message('Not enough space for new members!'.format(party_member.profession, party_member.name),
                              color=libtcod.lighter_blue)
            results = False
        return message, results
    
    def random_member(self):
        """
        Selects a random PartyMember from the list
        :return: PartyMember object
        """
        return choice(self.members)
    
    def kill_member(self, party_member):
        """
        Kill a party member: Remove a PartyMember from the list
        :param party_member: PartyMember object to remove from the party list
        :return: results of check for death
        """
        results = []
        
        self.members.remove(party_member)
        
        if not self.members:
            results.extend({'dead': self.owner})
        return results
    
    def remove_member(self, party_member):
        """
        Remove a PartyMember from the list
        :param party_member: PartyMember object to remove from the party list
        :return: results of check for death
        """
        results = []
        
        self.members.remove(party_member)
        results.append({'message': Message('{} {} removed from {}'.format(party_member.profession,
                                                                          party_member.name,
                                                                          self.owner.name),
                                           color=libtcod.lighter_blue)})
        if not self.members:
            results.append({'dead': self.owner})
        return results
    
    def random_member_no_cooldown(self):
        """
        Selects a random PartyMember from the list that is NOT on cooldown
        :return: PartyMember object
        """
        try:
            member = choice([member for member in self.members if member.cooldown <= 0])
            return member
        except IndexError:
            return None
    
    def tick_all(self, amount=1):
        """
        Iterate through all party members in list, ticking a turn off of their cooldown counter
        :param amount: int amount of turns to remove from cooldown for each PartyMember object
        :return: None
        """
        for member in self.members:
            member.tick(amount=amount)
    
    def add_coins(self, amount):
        """
        Add coins to the party's treasure horde
        :param amount:
        :return: None
        """
        self.coins += amount
        return Message(text='Hero Party found {} coins'.format(amount))
    
    def pay_members(self):
        """
        Remove coins from the party's treasure horde for each party member.
        If there are not enough coins to pay all party members, a random party member will be removed until there are
        :return: result list of messages
        """
        results = []
        while self.total_party_cost() > self.coins:
            person = self.random_member()
            results.append(Message(text="{} {} has left {} due to lack of funding".format(person.profession,
                                                                                          person.name,
                                                                                          self.owner.name),
                                   color=libtcod.orange))
            results.extend(self.remove_member(party_member=person))
        for member in self.members:
            results.append(Message(text="{} the {} gets paid {}".format(member.name, member.profession, member.cost)))
            self.coins -= member.get_cost()
        
        return results
    
    def total_party_cost(self):
        """
        Determine the total cost of payment for each party member
        :return: int total cost to pay
        """
        total_cost = 0
        for member in self.members:
            total_cost += member.get_cost()
        return total_cost


class PartyMember:
    def __init__(self, name, profession, offensive_cd, defensive_cd, attack_type, cost, cooldown=0):
        """
        Class to hold information for individual party members
        :param name: str name of party member
        :param profession: str profession of party member
        :param offensive_cd: int cooldown using ability/attack
        :param defensive_cd: int cooldown when party member gets hit
        :param attack_type: dependant on profession
        :param cost: int amount of gold paid out per turn time
        :param cooldown: int current cooldown
        """
        self.name = name
        self.profession = profession
        self.offensive_cd = offensive_cd
        self.defensive_cd = defensive_cd
        self.attack_type = attack_type
        self.cost = cost
        self.cooldown = cooldown
    
    def tick(self, amount=1):
        """
        Reduce cooldown for party member by amount number of turns (and don't go negative!)
        :param amount: int number of turns to reduce cooldown by
        :return: None
        """
        if self.cooldown > 0:
            self.cooldown -= amount
            if self.cooldown < 0:
                self.cooldown = 0
    
    def get_cost(self):
        """
        getter for cost
        :return: int cost in coins for party member
        """
        return self.cost
    
    def take_damage(self, modifier=0):
        """
        sets the cooldown when hit to the total of the defensive CD value and the modifier
        :param modifier: weaker or more powerful attacks can modify the base cooldown
        :return: None
        """
        self.cooldown = self.defensive_cd + modifier
    
    def attack(self, target):
        """
        Attack random member of enemy party not on cooldown.
        If all members of enemy party on cooldown, kills one at random.
        Puts attacker on cooldown
        :param target: Entity party being attacked
        :return: dict results of attack
        """
        results = []
        self.cooldown = self.offensive_cd
        
        # pick random member off cooldown
        member = target.party.random_member_no_cooldown()
        if member:
            results.append({'message': Message("{} {} stuns {} {} for {} turns".format(self.profession, self.name,
                                                                                       member.profession, member.name,
                                                                                       member.defensive_cd))})
            member.take_damage()
        else:
            # if all on cooldown, kill random member
            member = target.party.random_member()
            results.append({'message': Message("{} {} kills {} {}".format(self.profession, self.name,
                                                                          member.profession, member.name),
                                               libtcod.orange)})
            # removes member, checks for death
            results.extend(target.party.remove_member(member))
        
        return results
