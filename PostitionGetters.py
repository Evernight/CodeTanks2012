from math import degrees
from Geometry import Vector
from math import pi as PI
from MyUtils import bonus_name_by_type
from Position import Position

class GridPositionGetter:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def positions(self, tank, world):
        positions = []

        # Grid
        for i in range(self.width):
            for j in range(self.height):
                positions.append(
                    Position(
                        world.width * (1 + i) / (self.width + 1),
                        world.height * (1 + j) / (self.height + 1),
                        "GRID %s/%s, %s/%s" % (i + 1, self.width, j + 1, self.height))
                )

        return positions

class BorderPositionGetter:
    def __init__(self, width, height, distance):
        self.width = width
        self.height = height
        self.distance = distance

    def positions(self, tank, world):
        positions = []

        for i in range(self.width - 1):
            positions.append(Position(
                world.width * (1 + i) / (self.width + 1),
                world.height - self.distance,
                "LOW BORDER %s/%s" %(i + 1, self.width)))

            positions.append(Position(
                world.width * (1 + i) / (self.width + 1),
                self.distance,
                "TOP BORDER %s/%s" %(i + 1, self.width)))

        for j in range(self.height- 1):
            positions.append(Position(
                world.width - self.distance,
                world.height * (1 + j) / (self.height + 1),
                "RIGHT BORDER %s/%s" %(j + 1, self.height)))

            positions.append(Position(
                self.distance,
                world.height * (1 + j) / (self.height + 1),
                "LEFT BORDER %s/%s" %(j + 1, self.height)))


        return positions

class BasicPositionGetter:
    def __init__(self, short_direction=40, long_direction=80):
        self.short_direction = short_direction
        self.long_direction = long_direction

    def positions(self, tank, world):
        positions = []

        # Current position
        positions.append(Position(tank.x, tank.y, "CURRENT"))

        # Forward and back direction
        tank_v = Vector(tank.x, tank.y)
        tank_d_v = Vector(1, 0).rotate(tank.angle)
        forw = tank_v + tank_d_v * self.short_direction
        back = tank_v - tank_d_v * self.short_direction
        positions.append(Position(forw.x, forw.y, "FORWARD"))
        positions.append(Position(back.x, back.y, "BACKWARD"))

        fforw = tank_v + tank_d_v * self.long_direction
        fback = tank_v - tank_d_v * self.long_direction
        positions.append(Position(fforw.x, fforw.y, "FAR FORWARD"))
        positions.append(Position(fback.x, fback.y, "FAR BACKWARD"))

        # Low diagonal move
        DIAGONAL_ANGLE = PI/6
        for a in [DIAGONAL_ANGLE, - DIAGONAL_ANGLE, PI - DIAGONAL_ANGLE, DIAGONAL_ANGLE - PI]:
            pt = tank_v + tank_d_v.rotate(a) * 100
            positions.append(Position(pt.x, pt.y, "TURN %.0f" % degrees(a)))

        # Bonuses positions
        positions += [Position(b.x, b.y, "BONUS %s" % bonus_name_by_type(b.type)) for b in world.bonuses]

        return positions

class LightBasicPositionGetter:
    def positions(self, tank, world):
        positions = []

        # Current position
        positions.append(Position(tank.x, tank.y, "CURRENT"))

        # Forward and back direction
        tank_v = Vector(tank.x, tank.y)
        tank_d_v = Vector(1, 0).rotate(tank.angle)

        fforw = tank_v + tank_d_v * 80
        fback = tank_v - tank_d_v * 80
        positions.append(Position(fforw.x, fforw.y, "FAR FORWARD"))
        positions.append(Position(fback.x, fback.y, "FAR BACKWARD"))

        # Bonuses positions
        positions += [Position(b.x, b.y, "BONUS %s" % bonus_name_by_type(b.type)) for b in world.bonuses]

        return positions

class TrivialPositionGetter:
    def positions(self, tank, world):
        positions = []
        # Current position
        positions.append(Position(tank.x, tank.y, "CURRENT"))
        positions += [Position(b.x, b.y, "BONUS %s" % bonus_name_by_type(b.type)) for b in world.bonuses]

        return positions




class MainDirectionsGetter:
    def positions(self, tank, world):
        positions = []

        # Forward and back direction
        tank_v = Vector(tank.x, tank.y)
        tank_d_v = Vector(1, 0).rotate(tank.angle)

        forw = tank_v + tank_d_v * 40
        back = tank_v - tank_d_v * 40
        positions.append(Position(forw.x, forw.y, "FORWARD"))
        positions.append(Position(back.x, back.y, "BACKWARD"))

        fforw = tank_v + tank_d_v * 80
        fback = tank_v - tank_d_v * 80
        positions.append(Position(fforw.x, fforw.y, "FAR FORWARD"))
        positions.append(Position(fback.x, fback.y, "FAR BACKWARD"))

        return positions

class BonusPositionGetter:
    def positions(self, tank, world):
        return [Position(b.x, b.y, "BONUS %s" % bonus_name_by_type(b.type)) for b in world.bonuses]

class LowDiagonalGetter:
    def __init__(self, angle=PI/6):
        self.angle = angle

    def positions(self, tank, world):
        positions = []

        # Low diagonal move
        tank_v = Vector(tank.x, tank.y)
        tank_d_v = Vector(1, 0).rotate(tank.angle)

        for a in [self.angle, - self.angle, PI - self.angle, self.angle - PI]:
            pt = tank_v + tank_d_v.rotate(a) * 100
            positions.append(Position(pt.x, pt.y, "TURN %.0f" % degrees(a)))
        return positions