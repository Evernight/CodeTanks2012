from math import fabs, pi as PI

class TargetEstimator:
    context = None

class AnglePenaltyTEstimator(TargetEstimator):
    NAME = "Angle"

    def value(self, target):
        angle_penalty_factor = (1 + (1 - self.context.health_fraction) * 1.5 -
                                (1 - max(0, 150 - self.context.tank.remaining_reloading_time)/150) * 1)
        angle_degrees = fabs(self.context.tank.get_turret_angle_to_unit(target)) / PI * 180
        angle_penalty = angle_penalty_factor * (angle_degrees**1.2)/2
        return angle_penalty

class DistancePenaltyTEstimator(TargetEstimator):
    NAME = "Distance"

    def value(self, target):
        distance_penalty = self.context.tank.get_distance_to_unit(target) / 10
        return distance_penalty

class FinishTEstimator(TargetEstimator):
    NAME = "Finish"

    def value(self, target):
        if ((target.crew_health <= 20 or target.hull_durability <= 20) or
            (self.context.tank.premium_shell_count > 0 and (target.crew_health <= 35 or target.hull_durability <= 35))):
            finish_bonus = 30
        else:
            finish_bonus = 0
        return finish_bonus

class ResponseTEstimator(TargetEstimator):
    NAME = "Response"

    def value(self, target):
        tank = self.context.tank
        if self.context.physics.attacked_area(tank.x, tank.y, target, cache=self.context.EA_cache) > 0.5:
            attacking_me_bonus = 20
        else:
            attacking_me_bonus = 0
        return attacking_me_bonus

class LastTargetTEstimator(TargetEstimator):
    NAME = "Last Target"

    def value(self, target):
        last_target_bonus = 0
        if self.context.memory.last_turret_target_id:
            if self.context.memory.last_turret_target_id == target.id:
                last_target_bonus = 5
        return last_target_bonus

class AddConstantTEstimator(TargetEstimator):
    NAME = "C"

    def value(self, target):
        return 180