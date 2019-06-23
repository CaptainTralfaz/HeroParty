class Entity:
    def __init__(self, x, y, char, color, name, blocks=False):
        """
        A generic object to represent players, enemies, items, etc.
        :param x: horizontal position on map
        :param y: vertical position on map
        :param char: character representing the Entity
        :param color: color of the character
        :param name: string name of the Entity
        :param blocks: True if Entity blocks movement of other Entities
        """
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
    
    def move(self, dx, dy):
        """
        Change x and y coordinates of Entity object
        :param dx: int direction on x axis
        :param dy: int direction on y axis
        :return: None
        """
        self.x += dx
        self.y += dy


def get_blocking_entities_at_location(entities, x, y):
    """
    Returns blocking entity in a location
    :param entities: list of Entity objects
    :param x: horizontal location
    :param x: vertical location
    :return: blocking Entity object in destination (x, y) or None if no Entity object in destination block movement
    """
    for entity in entities:
        if entity.blocks and entity.x == x and entity.y == y:
            return entity
    
    return None
