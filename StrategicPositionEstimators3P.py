from math import fabs
from GamePhysics import MAX_DISTANCE
from Geometry import Vector
from MyUtils import ALLY_TANK, target_dangerousness_for_tank
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

class AlliesDistance3P(PositionEstimator):
    NAME = 'Too close'

    def __init__(self, close_distance, close_distance_penalty, far_distance, far_distance_penalty):
        self.close_distance = close_distance
        self.close_distance_penalty = close_distance_penalty
        self.far_distance = far_distance
        self.far_distance_penalty = far_distance_penalty

    def value(self, pos):
        allies = self.context.allies

        result = 0
        for ally in allies:
            dist = ally.get_distance_to(pos.x, pos.y)
            if dist < self.close_distance:
                result += -self.close_distance_penalty * (1 - dist/self.close_distance)
            result -= max(0, dist - self.far_distance)/(1500 - self.far_distance) * self.far_distance_penalty

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
            result += ring_linear_bonus((0.25 + 0.75 * enemy_health) * self.max_distance + (1 - self.context.health_fraction**1.2) * self.max_distance/2,
                                        self.radius, self.max_value, dist) / len(enemies) * 0.5

            # Spread it onto all field
            result += ring_linear_bonus((0.25 + 0.75 * enemy_health) * self.max_distance + (1 - self.context.health_fraction**1.2) * self.max_distance/2,
                                        MAX_DISTANCE/2, self.max_value, dist) / len(enemies) * 0.5
            #result = max(result, (1 - dist / MAX_DISTANCE) * self.max_value / len(enemies))

        return result

class BeAroundWeakestEnemyV2(PositionEstimator):
    NAME = 'Around enemy'

    def __init__(self, max_value, max_distance, radius, tank_dependent_distance):
        self.max_value = max_value
        self.max_distance = max_distance
        self.radius = radius
        self.tank_dependent_distance = tank_dependent_distance

    def value(self, pos):
        enemies = self.context.enemies

        result = 0
        for enemy in enemies:
            dist = enemy.get_distance_to(pos.x, pos.y)
            optimal_distance = max(0, min(1000, self.max_distance + self.tank_dependent_distance * target_dangerousness_for_tank(enemy, self.context.tank)))

            result += ring_linear_bonus(optimal_distance,
                self.radius, self.max_value, dist) / len(enemies) * 0.5

            # Spread it onto all field
            result += ring_linear_bonus(optimal_distance,
                MAX_DISTANCE/2, self.max_value, dist) / len(enemies) * 0.5
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
            enemy_v = Vector(enemy.x, enemy.y)

            if self.context.physics.vector_is_intersecting_object(pos_v , enemy_v - pos_v , obstacle, 1.05):
                if self.context.health_fraction <= 0.3 or tank.remaining_reloading_time > 100:
                    result += self.max_value
                else:
                    result -= self.max_value

        return result

class CenterObstaclePenalty(PositionEstimator):
    NAME = 'Obstacle'

    def __init__(self, max_value=5000, radius=10):
        self.max_value = max_value
        self.radius = radius

    def value(self, pos):
        obstacle = self.context.world.obstacles[0]

        vd = fabs(obstacle.y - pos.y)
        hd = fabs(obstacle.x - pos.x)
        if vd < obstacle.height + self.radius and hd < obstacle.width + self.radius:
            return -self.max_value
        return 0