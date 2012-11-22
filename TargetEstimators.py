from math import fabs, pi as PI, sqrt, cos
from GamePhysics import SHELL_ACCELERATION, INITIAL_SHELL_VELOCITY, LOW_ANGLE, FICTIVE_ACCELERATION
from Geometry import Vector
from MyUtils import solve_quadratic, fictive_unit, estimate_target_dangerousness, target_dangerousness_for_tank
from TargetingClasses import get_target_data

class TargetEstimator:
    context = None
    debugging = False
    def value(self, target):
        return 0

class AnglePenaltyTEstimator(TargetEstimator):
    NAME = "Angle"

    def value(self, target):
        angle_penalty_factor = (1 + (1 - self.context.health_fraction) * 1.5 -
                                (1 - max(0, 150 - self.context.tank.remaining_reloading_time)/150) * 1)
        angle_degrees = fabs(self.context.tank.get_turret_angle_to_unit(target)) / PI * 180
        angle_penalty = angle_penalty_factor * (angle_degrees**1.2)/2
        return -angle_penalty

class DistancePenaltyTEstimator(TargetEstimator):
    NAME = "Distance"

    def value(self, target):
        distance_penalty = self.context.tank.get_distance_to_unit(target) / 10
        return -distance_penalty

class FinishTEstimator(TargetEstimator):
    NAME = "Finish"

    def __init__(self, max_value):
        self.max_value = max_value

    def value(self, target):
        if ((target.crew_health <= 20 or target.hull_durability <= 20) or
            (self.context.tank.premium_shell_count > 0 and (target.crew_health <= 35 or target.hull_durability <= 35))):
            finish_bonus = self.max_value
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

    def __init__(self, max_value):
        self.max_value = max_value

    def value(self, target):
        return self.max_value

class AttackWeakestTEstimator(TargetEstimator):
    NAME = "Weakest"

    def __init__(self, max_value):
        self.max_value = max_value

    def value(self, target):
        weakest_bonus = (1 - target.crew_health / target.crew_max_health) * self.max_value
        return weakest_bonus

class BehindObstacleTEstimator(TargetEstimator):
    NAME = "Blocked"

    def __init__(self, max_value):
        self.max_value = max_value

    def value(self, target):
        tank = self.context.tank

        target_v = Vector(target.x, target.y)
        tank_v = Vector(tank.x, tank.y)
        penalty = 0
        obstacle = self.context.world.obstacles[0]
        if self.context.physics.vector_is_intersecting_object(tank_v , target_v - tank_v, obstacle, 1.05):
            penalty = self.max_value
        return -penalty

class DebugTargetSpeedTEstimator(TargetEstimator):
    NAME = "Speed"
    debugging = True

    def debug_value(self, target):
        target_speed = Vector(target.speedX, target.speedY)
        return "%4.2f" % target_speed.length()

FICTIVE_TARGET_ACCELERATION = 0.08
MAX_TARGET_SPEED = 4
class DebugVarianceTEstimator(TargetEstimator):
    NAME = "Variance"
    debugging = True

    def debug_value(self, target):
        tank = self.context.tank
        physics = self.context.physics

        b = tank.angle + tank.turret_relative_angle
        e = Vector(1, 0)
        q = e.rotate(b)

        target_v = Vector(target.x, target.y)
        target_direction = Vector(1, 0).rotate(target.angle)
        target_speed = Vector(target.speedX, target.speedY)

        def get_hit_time():
            v0 = INITIAL_SHELL_VELOCITY
            a = SHELL_ACCELERATION
            d = max(0, tank.get_distance_to_unit(target) - 60)
            return solve_quadratic(a/2, v0, -d)

        def max_move_distance(v0, a, max_v, t):
            #TODO: this estimation is rough
            v0 = max(-max_v, min(v0, max_v))
            if fabs(v0 + a * t) > max_v:
                if a > 0:
                    t1 = fabs((max_v - v0) / a)
                else:
                    t1 = fabs((-max_v - v0) / a)
                t2 = t - t1
            else:
                t1 = t
                t2 = 0
            if a > 0:
                return a*t1**2/2 + v0 * t1 + max_v * t2
            else:
                return a*t1**2/2 + v0 * t1 - max_v * t2

        t = get_hit_time()
        center = Vector(target.x - tank.x, target.y - tank.y)

        v0 = target_speed.projection(target_direction)
        target_avoid_distance_forward = max_move_distance(v0, FICTIVE_TARGET_ACCELERATION, MAX_TARGET_SPEED, t)
        target_avoid_distance_backward = max_move_distance(v0, -FICTIVE_TARGET_ACCELERATION * 0.75, MAX_TARGET_SPEED, t)
        max_pos = target_v + target_avoid_distance_forward * target_direction
        min_pos = target_v + target_avoid_distance_backward * target_direction

        target_turret_n_cos = fabs(cos(fabs(b - target.angle) + PI/2))

        var = fabs((target_avoid_distance_forward - target_avoid_distance_backward) * target_turret_n_cos)

        estimate_pos = target_v + target_direction * ((target_avoid_distance_forward + target_avoid_distance_backward) / 2)
        vulnerable_width = max(90 * target_turret_n_cos, 60 * (1 - target_turret_n_cos))

        shoot = physics.will_hit(tank, fictive_unit(target, max_pos.x, max_pos.y)) and physics.will_hit(tank, fictive_unit(target, min_pos.x, min_pos.y))

        return "fw=%s, bw=%s, t=%s, var=%s, wid=%s, degree=%s, shoot=%s" % (int(target_avoid_distance_forward), int(target_avoid_distance_backward), int(t), int(var), vulnerable_width,
                                                                            fabs(tank.get_turret_angle_to(estimate_pos.x, estimate_pos.y)) / PI * 180, shoot)

class DebugSmartShootingTEstimator(TargetEstimator):
    NAME = "Debug"
    debugging = True

    def debug_value(self, target):
        self.physics = self.context.physics
        self.cur_target = target
        self.world = self.context.world
        self.tank = self.context.tank
        self.memory = self.context.memory

        return str(get_target_data(self))

class DebugDangerousnessTEstimator(TargetEstimator):
    NAME = "Dangerous"
    debugging = True

    def debug_value(self, target):
        self.physics = self.context.physics
        self.cur_target = target
        self.world = self.context.world
        self.tank = self.context.tank
        self.memory = self.context.memory

        return "%8.2f" % target_dangerousness_for_tank(target, self.tank)


class TargetConvenienceEstimator(TargetEstimator):
    NAME = "Convenience"

    def __init__(self, max_value):
        self.max_value = max_value

    def value(self, target):
        tank = self.context.tank

        tank_v = Vector(tank.x, tank.y)
        target_v = Vector(target.x, target.y)

        #b = tank.angle + tank.turret_relative_angle
        b = (target_v - tank_v).angle(Vector(1, 0))

        target_direction = Vector(1, 0).rotate(target.angle)
        target_speed = Vector(target.speedX, target.speedY)

        def get_hit_time():
            v0 = INITIAL_SHELL_VELOCITY
            a = SHELL_ACCELERATION
            d = max(0, tank.get_distance_to_unit(target) - 60)
            return solve_quadratic(a/2, v0, -d)

        def max_move_distance(v0, a, max_v, t):
            v0 = max(-max_v, min(v0, max_v))
            if fabs(v0 + a * t) > max_v:
                if a > 0:
                    t1 = fabs((max_v - v0) / a)
                else:
                    t1 = fabs((-max_v - v0) / a)
                t2 = t - t1
            else:
                t1 = t
                t2 = 0
            if a > 0:
                return a*t1**2/2 + v0 * t1 + max_v * t2
            else:
                return a*t1**2/2 + v0 * t1 - max_v * t2

        t = get_hit_time()

        v0 = target_speed.projection(target_direction)
        target_health_fraction = target.crew_health/target.crew_max_health
        efficency = (1 + target_health_fraction)/2

        target_avoid_distance_forward = max_move_distance(v0, FICTIVE_TARGET_ACCELERATION * efficency, MAX_TARGET_SPEED * efficency, t)
        target_avoid_distance_backward = max_move_distance(v0, -FICTIVE_TARGET_ACCELERATION * 0.75 * efficency, MAX_TARGET_SPEED * efficency, t)

        target_turret_n_cos = fabs(cos(fabs(b - target.angle) + PI/2))

        var = fabs((target_avoid_distance_forward - target_avoid_distance_backward) * target_turret_n_cos)

        return (1 - var/200) * self.max_value