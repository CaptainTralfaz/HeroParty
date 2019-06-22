class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def move(self, dx, dy):
        """
        Change x and y coordinates of entity
        :param dx: int direction on x axis
        :param dy: int direction on y axis
        :return: None
        """
        # Move the entity by a given amount
        self.x += dx
        self.y += dy
