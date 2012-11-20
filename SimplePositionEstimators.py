from PositionEstimators import PositionEstimator
from math import sqrt
from MyUtils import unit_closest_to
from model.BonusType import BonusType

class StoppingPenaltyEstimator(PositionEstimator):
    def value(self, pos):
        stopping_penalty = (1 + 2 * max(0, 100 - self.context.tank.get_distance_to(pos.x, pos.y)))**1.2
        return stopping_penalty

class BonusPositionEstimator(PositionEstimator):
    """
    Bonus priority:
    + Need this bonus
    (*) - Close to enemy going for it
    """
    NAME = 'Bonus'

    def __init__(self, medikit_min=250, medikit_max=1500, repair_min=100, repair_max=800, ammo_crate=500, factor=1):
        self.medikit_min = medikit_min
        self.medikit_max = medikit_max
        self.repair_min = repair_min
        self.repair_max = repair_max
        self.ammo_crate = ammo_crate

        self.factor = factor

    def value(self, pos):
        try:
            closest_bonus = unit_closest_to(pos.x, pos.y)(self.context.world.bonuses)

            if closest_bonus.type == BonusType.MEDIKIT:
                bonus_profit = self.medikit_min + sqrt(1 - self.context.health_fraction) * (self.medikit_max - self.medikit_min)
            elif closest_bonus.type == BonusType.REPAIR_KIT:
                bonus_profit = self.repair_min + sqrt(1 - self.context.hull_fraction) * (self.repair_max - self.repair_min)
            elif closest_bonus.type == BonusType.AMMO_CRATE:
                bonus_profit = self.ammo_crate
            else:
                bonus_profit = 0

            bonus_summand = max(0, bonus_profit)

            if closest_bonus.get_distance_to(pos.x, pos.y) > 10:
                bonus_summand = 0
        except:
            bonus_summand = 0
        return bonus_summand * self.factor

class TimeToPositionEstimator(PositionEstimator):
    NAME = 'Time'

    def __init__(self, factor):
        self.factor = factor

    def value(self, pos):
        if not pos in self.context.est_time_cache:
            self.context.est_time_cache[pos] = self.context.physics.estimate_time_to_position(pos.x, pos.y, self.context.tank)
        return -self.context.est_time_cache[pos] * self.factor

MIN_EDGE_DISTANCE = 20
class EdgePenaltyEstimator(PositionEstimator):
    """
    Don't stick to fucking edges
    """
    # TODO: relate to bonus
    NAME = 'Edges'

    def __init__(self, border_value, width):
        self.border_value = border_value
        self.width = width

        self.c = width**2/border_value

    def value(self, pos):
        edges_penalty = max(0, -self.context.physics.distance_to_edge(pos.x, pos.y, self.context.world)**2/self.c + self.border_value)
        if pos.x < MIN_EDGE_DISTANCE or pos.y < MIN_EDGE_DISTANCE or pos.x > self.context.world.width - MIN_EDGE_DISTANCE or pos.y > self.context.world.height - MIN_EDGE_DISTANCE:
            edges_penalty = 5000
        return -edges_penalty

class LinearEdgePenaltyEstimator(PositionEstimator):
    NAME = 'Edges'

    def __init__(self, border_value, width):
        self.border_value = border_value
        self.width = width

        self.c = width/border_value

    def value(self, pos):
        edges_penalty = max(0, -self.context.physics.distance_to_edge(pos.x, pos.y, self.context.world)/self.c + self.border_value)
        if pos.x < MIN_EDGE_DISTANCE or pos.y < MIN_EDGE_DISTANCE or pos.x > self.context.world.width - MIN_EDGE_DISTANCE or pos.y > self.context.world.height - MIN_EDGE_DISTANCE:
            edges_penalty = 5000
        return -edges_penalty

class LastTargetEstimator(PositionEstimator):
    NAME = 'Last_Target'

    def __init__(self, max_value):
        self.max_value = max_value

    def value(self, pos):
        last_target = self.context.memory.last_target_position.get(self.context.tank.id)
        if (last_target and last_target.distance(pos.x, pos.y) < 10
            and last_target.distance(self.context.tank.x, self.context.tank.y) > 30):
            prev_target_bonus = self.max_value
        else:
            prev_target_bonus = 0
        return prev_target_bonus

class FlyingShellEstimator(PositionEstimator):
    """
    + Flying shells
    """
    NAME = 'Shells'

    def __init__(self, max_value):
        self.max_value = max_value

    def value(self, pos):
        flying_shell_penalty = 0
        if not pos in self.context.est_time_cache:
            self.context.est_time_cache[pos] = self.context.physics.estimate_time_to_position(pos.x, pos.y, self.context.tank)
        est_time = self.context.est_time_cache[pos]

        for shell in self.context.world.shells:
            if self.context.physics.shell_will_hit_tank_going_to(shell, self.context.tank, pos.x, pos.y, et=est_time):
                flying_shell_penalty += self.max_value
        return -flying_shell_penalty

class AddConstantEstimator(PositionEstimator):
    NAME = "C"

    def __init__(self, max_value):
        self.max_value = max_value

    def value(self, pos):
        return self.max_value