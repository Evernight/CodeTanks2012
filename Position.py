from math import hypot

class Position:
    def __init__(self,x, y, name):
        self.x = x
        self.y = y
        self.name = name

    def __str__(self):
        return 'POS [%20s] (%8.2f, %8.2f)' % (self.name, self.x, self.y)

    def distance(self, x, y):
        return hypot(self.x - x, self.y - y)

    def __hash__(self):
        return (self.x, self.y).__hash__()