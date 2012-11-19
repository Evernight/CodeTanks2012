from math import fabs
from MyUtils import ALLY_TANK
from PositionEstimators import PositionEstimator

class CloseDistancePenalty3P(PositionEstimator):
    NAME = 'Too close'

    def __init__(self, close_distance, close_distance_penalty):
        self.close_distance = close_distance
        self.close_distance_penalty = close_distance_penalty

    def value(self, pos):
        tanks = self.context.world.tanks
        cur_tank = self.context.tank

        allies = list(filter(ALLY_TANK(cur_tank.id), tanks))

        result = 0
        for ally in allies:
            dist = ally.get_distance_to(pos.x, pos.y)
            if dist < self.close_distance:
                result += -self.close_distance_penalty * (1 - dist/self.close_distance)

        return result