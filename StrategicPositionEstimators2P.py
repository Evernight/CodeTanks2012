from math import fabs
from MyUtils import ALLY_TANK
from PositionEstimators import PositionEstimator

class Distance2PEstimator(PositionEstimator):
    NAME = '2P distance'

    def __init__(self, max_value, width, optimal_distance, close_distance=100, close_distance_penalty=0):
        self.max_value = max_value
        self.width = width
        self.optimal_distance = optimal_distance

        self.close_distance = close_distance
        self.close_distance_penalty = close_distance_penalty

    def value(self, pos):
        result = 0

        tanks = self.context.world.tanks
        cur_tank = self.context.tank

        allies = list(filter(ALLY_TANK(cur_tank.id), tanks))
        if len(allies) != 1:
            return 0
        ally = allies[0]
        dist = ally.get_distance_to(pos.x, pos.y)

        result = max(0, (1 - fabs(dist - self.optimal_distance)/self.width)) * self.max_value
        if dist < self.close_distance:
            result = -self.close_distance_penalty * (1 - dist/self.close_distance)

        return result

class FarDistancePenalty2P(PositionEstimator):
    NAME = '2P far'

    def __init__(self, danger_dist, max_value):
        self.max_value = max_value
        self.danger_dist = danger_dist

    def value(self, pos):
        tanks = self.context.world.tanks
        cur_tank = self.context.tank

        allies = list(filter(ALLY_TANK(cur_tank.id), tanks))
        if len(allies) != 1:
            return 0
        ally = allies[0]
        dist = ally.get_distance_to(pos.x, pos.y)

        return -max(0, dist - self.danger_dist)/(1500 - self.danger_dist) * self.max_value
