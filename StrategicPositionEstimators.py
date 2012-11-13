from math import sqrt
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
