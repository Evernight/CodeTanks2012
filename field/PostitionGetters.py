from math import degrees
from Geometry import Vector
from math import pi as PI
from MyUtils import bonus_name_by_type
from field.Position import Position

GRID_HOR_COUNT = 7
GRID_VERT_COUNT = 5
class BasicPositionGetter:
    def positions(self, tank, world):
        positions = []

        # Grid
        for i in range(GRID_HOR_COUNT):
            for j in range(GRID_VERT_COUNT):
                if (i > 1 and i < 5) and (j == 2):
                    continue
                positions.append(
                    Position(
                        world.width * (1 + i) / (GRID_HOR_COUNT + 1),
                        world.height * (1 + j) / (GRID_VERT_COUNT + 1),
                        "GRID %s, %s" % (i, j))
                )

        # Current position
        positions.append(Position(tank.x, tank.y, "CURRENT"))

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

        # Low diagonal move
        DIAGONAL_ANGLE = PI/6
        for a in [DIAGONAL_ANGLE, - DIAGONAL_ANGLE, PI - DIAGONAL_ANGLE, DIAGONAL_ANGLE - PI]:
            pt = tank_v + tank_d_v.rotate(a) * 100
            positions.append(Position(pt.x, pt.y, "TURN %.0f" % degrees(a)))

        # Bonuses positions
        positions += [Position(b.x, b.y, "BONUS %s" % bonus_name_by_type(b.type)) for b in world.bonuses]

        return positions