from math import fabs
from MyUtils import ALLY_TANK
from field.PositionEstimators import PositionEstimator

class Distance2PEstimator(PositionEstimator):
    """
    How dangerous position is
    + In centre of massacre
    + Turrets directed
    """
    NAME = '2P distance'

    def __init__(self, max_value, width, optimal_distance):
        self.max_value = max_value
        self.width = width
        self.optimal_distance = optimal_distance

    def value(self):
        tanks = self.context.world.tanks
        cur_tank = self.context.tank

        allies = list(filter(ALLY_TANK(cur_tank.id), tanks))
        if len(allies) != 1:
            return 0
        ally = allies[0]
        dist = ally.get_distance_to_unit(cur_tank)

        return (1 - fabs(dist - self.optimal_distance)/self.width) * self.max_value
