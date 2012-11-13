from math import sqrt, fabs
from GamePhysics import MAX_DISTANCE
from Geometry import Vector
from PositionEstimators import PositionEstimator

class PositionalDangerEstimator(PositionEstimator):
    """
    How dangerous position is
    + In centre of massacre
    + Turrets directed
    """
    NAME = 'Positional'

    def value(self, pos):
        try:
            positional_danger_penalty = - sqrt(sum(map(lambda enemy: enemy.get_distance_to(pos.x, pos.y)**2, self.context.enemies))/self.context.enemies_count)
        except:
            self.context.debug("!!! All enemies were destroyed")
            positional_danger_penalty = 0
        positional_danger_penalty += 700

        danger_penalty_factor = {
                                    5 : 5,
                                    4 : 4,
                                    3 : 3,
                                    2 : 1,
                                    1 : 0.3
                                }[self.context.enemies_count]
        if self.context.enemies_count == 1 and self.context.health_fraction >= 0.7 and self.context.hull_fraction >= 0.5:
            enemy_tank = self.context.enemies[0]
            if enemy_tank.crew_health < 40 or enemy_tank.hull_durability < 20:
                # BLOODLUST
                danger_penalty_factor = -3
            else:
                danger_penalty_factor = 0

        positional_danger_penalty *= danger_penalty_factor
        return -positional_danger_penalty

class TurretsDangerEstimator(PositionEstimator):
    NAME = 'Turrets'

    def value(self, pos):
        turrets_danger_penalty = 0
        for enemy in self.context.enemies:
            turrets_danger_penalty += self.context.physics.attacked_area(pos.x, pos.y, enemy, cache=self.context.EA_cache)

        turrets_danger_penalty_factor = {
                                            5 : 100,
                                            4 : 100,
                                            3 : 200,
                                            2 : 300,
                                            1 : 350
                                        }[len(self.context.enemies)]
        turrets_danger_penalty *= turrets_danger_penalty_factor
        return -turrets_danger_penalty

class PositionalPairDangerEstimator(PositionEstimator):
    NAME = 'PairPos'

    def __init__(self, max_value):
        self.max_value = max_value

    def _get_danger(self, pos, tank1, tank2):
        tank1_v = Vector(tank1.x, tank1.y)
        tank2_v = Vector(tank2.x, tank2.y)
        tank_v = Vector(pos.x, pos.y)

        d1 = (tank1_v - tank_v).normalize()
        d2 = (tank2_v - tank_v).normalize()
        # the more 'danger' is, the more dangerous position is. Values: [0..1]
        danger = fabs(1 - d1.scalar_product(d2))/2

        return sqrt(danger)

    def value(self, pos):
        positional_danger = 0
        try:
            enemies = self.context.enemies
            if len(enemies) < 2:
                return 0
            max_sum = 0
            for i, e1 in enumerate(enemies):
                for e2 in enemies[(i + 1):]:
                    dist = e1.get_distance_to_unit(e2)
                    positional_danger += self._get_danger(pos, e1, e2) / dist
                    max_sum += 1/dist
            positional_bonus = (1 - positional_danger/max_sum) * self.max_value
        except:
            positional_bonus = 0
        return positional_bonus

class PositionalPairDangerEstimatorWODist(PositionEstimator):
    NAME = 'PairPos'

    def __init__(self, max_value):
        self.max_value = max_value

    def _get_danger(self, pos, tank1, tank2):
        tank1_v = Vector(tank1.x, tank1.y)
        tank2_v = Vector(tank2.x, tank2.y)
        tank_v = Vector(pos.x, pos.y)

        d1 = (tank1_v - tank_v).normalize()
        d2 = (tank2_v - tank_v).normalize()
        # the more 'danger' is, the more dangerous position is. Values: [0..1]
        danger = fabs(1 - d1.scalar_product(d2))/2

        return sqrt(danger)

    def value(self, pos):
        positional_danger = 0
        try:
            enemies = self.context.enemies
            if len(enemies) < 2:
                return 0
            for i, e1 in enumerate(enemies):
                for e2 in enemies[(i + 1):]:
                    positional_danger += self._get_danger(pos, e1, e2)
            positional_bonus = (1 - positional_danger) * self.max_value
        except:
            positional_bonus = 0
        return positional_bonus


class PositionalPowerDangerEstimator(PositionEstimator):
    NAME = 'PosPower'

    def __init__(self, power, max_value):
        self.power = power
        self.max_possible = MAX_DISTANCE**(2 * self.power)
        self.max_value = max_value

    def value(self, pos):
        try:
            enemies = self.context.enemies
            safety = sum([((e.x - pos.x)**2 + (e.y - pos.y)**2)**self.power for e in enemies])/(self.context.enemies_count * self.max_possible)
            positional_bonus = safety * self.max_value
        except:
            positional_bonus = 0
        return positional_bonus