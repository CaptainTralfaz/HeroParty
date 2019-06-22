class Rect:
    def __init__(self, x, y, w, h):
        """
        Basic class for holding a rectangle
        :param x: top left x coordinate
        :param y: top left y coordinate
        :param w: width
        :param h: height
        """
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
    
    def center(self):
        """
        Determine center coordinate of a room (round down)
        :return: center coordinate x and y
        """
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return center_x, center_y
    
    def intersect(self, other):
        """
        returns true if this rectangle intersects with another one
        :param other: another Rect object
        :return: boolean true if two rooms intersect
        """
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)
