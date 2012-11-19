from math import fabs
from GamePhysics import MAX_DISTANCE
from MyUtils import ALLY_TANK
from PositionEstimators import PositionEstimator

class CloseDistancePenalty3P(PositionEstimator):
    NAME = 'Too close'

    def __init__(self, close_distance, close_distance_penalty):
        self.close_distance = close_distance
        self.close_distance_penalty = close_distance_penalty

    def value(self, pos):
        allies = self.context.allies

        result = 0
        for ally in allies:
            dist = ally.get_distance_to(pos.x, pos.y)
            if dist < self.close_distance:
                result += -self.close_distance_penalty * (1 - dist/self.close_distance)

        return result


class RunForEnemy(PositionEstimator):
    NAME = 'Go to enemy'

    def __init__(self, max_value):
        self.max_value = max_value

    def value(self, pos):
        enemies = self.context.enemies

        result = 0
        for enemy in enemies:
            dist = enemy.get_distance_to(pos.x, pos.y)
            result += dist / MAX_DISTANCE * self.max_value / len(enemies)

        return result