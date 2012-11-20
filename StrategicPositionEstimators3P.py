from math import fabs
from GamePhysics import MAX_DISTANCE
from Geometry import Vector
from MyUtils import ALLY_TANK
from PositionEstimators import PositionEstimator, ring_linear_bonus

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
            result = max(result, (1 - dist / MAX_DISTANCE) * self.max_value / len(enemies))

        return result

class BeAroundWeakestEnemy(PositionEstimator):
    NAME = 'Around enemy'

    def __init__(self, max_value, max_distance, radius):
        self.max_value = max_value
        self.max_distance = max_distance
        self.radius = radius

    def value(self, pos):
        enemies = self.context.enemies

        result = 0
        for enemy in enemies:
            enemy_health = enemy.crew_health/enemy.crew_max_health

            dist = enemy.get_distance_to(pos.x, pos.y)
            result += ring_linear_bonus(enemy_health * self.max_distance + (1 - self.context.health_fraction) * self.max_distance/2,
                                        self.radius, self.max_value, dist) / len(enemies)
            #result = max(result, (1 - dist / MAX_DISTANCE) * self.max_value / len(enemies))

        return result


class HideBehindObstacle(PositionEstimator):
    NAME = 'Hide'

    def __init__(self, max_value):
        self.max_value = max_value

    def value(self, pos):
        enemies = self.context.enemies
        tank = self.context.tank

        pos_v = Vector(pos.x, pos.y)
        result = 0
        obstacle = self.context.world.obstacles[0]
        for enemy in enemies:
            enemy_v = Vector(enemy.x, enemy. y)

            if self.context.physics.vector_is_intersecting_object(pos_v , enemy_v - pos_v , obstacle, 1.1):
                if self.context.health_fraction <= 0.3 or tank.remaining_reloading_time > 100:
                    result += self.max_value
                else:
                    result -= self.max_value

        return result