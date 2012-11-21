from itertools import chain
from math import fabs, cos
from GamePhysics import INITIAL_SHELL_VELOCITY, SHELL_ACCELERATION
from Geometry import sign, Vector
from MyUtils import DEAD_TANK, ALLY_TANK, fictive_unit, solve_quadratic, inverse_dict, index_in_sorted
from model.FireType import FireType
from math import pi as PI

class ShootDecisionMaker:
    context = None

# ================ CONSTANTS
# Targeting
TARGETING_FACTOR = 0.3
BONUS_FACTOR = 1.25
DEAD_TANK_OBSTACLE_FACTOR = 1.15
class OldShootDecisionMaker(ShootDecisionMaker):
    def process(self, cur_target, move):
        tank = self.context.tank
        world = self.context.world
        self.physics = self.context.physics
        world = self.context.world

        est_pos = self.physics.estimate_target_position(cur_target, tank)

        def bonus_is_attacked():
            for bonus in world.bonuses:
                if (self.physics.will_hit(tank, bonus, BONUS_FACTOR) and
                    tank.get_distance_to_unit(bonus) < tank.get_distance_to(*est_pos)):
                    return bonus
            return False

        def obstacle_is_attacked():
            obstacles = chain(
                filter(DEAD_TANK, world.tanks),
                filter(ALLY_TANK(tank.id), world.tanks),
                world.obstacles
            )
            for obstacle in obstacles:
                next_position = self.physics.estimate_target_position(obstacle, tank)
                next_unit = fictive_unit(obstacle, next_position[0], next_position[1])

                blocked = ((self.physics.will_hit(tank, next_unit, DEAD_TANK_OBSTACLE_FACTOR)
                            or self.physics.will_hit(tank, obstacle, DEAD_TANK_OBSTACLE_FACTOR))
                           and tank.get_distance_to_unit(obstacle) < tank.get_distance_to(*est_pos))
                if blocked:
                    return obstacle
            return False

        cur_angle = tank.get_turret_angle_to(*est_pos)
        good_to_shoot = self.physics.will_hit(
            tank,
            fictive_unit(cur_target, est_pos[0], est_pos[1]),
            TARGETING_FACTOR
        )
        if good_to_shoot:
            if self.context.health_fraction > 0.8 and self.context.hull_fraction > 0.5 and tank.get_distance_to_unit(cur_target) > 400 and tank.premium_shell_count <= 3:
                move.fire_type = FireType.REGULAR
            else:
                move.fire_type = FireType.PREMIUM_PREFERRED
        else:
            move.fire_type = FireType.NONE

        if bonus_is_attacked() or obstacle_is_attacked():
            self.context.debug('!!! Obstacle is attacked, don\'t shoot')
            move.fire_type = FireType.NONE

        if world.tick < 10 + tank.teammate_index * 10:
            move.fire_type = FireType.NONE

        if fabs(cur_angle) > PI/180 * 0.5:
            move.turret_turn = sign(cur_angle)

FICTIVE_TARGET_ACCELERATION = 0.1
MAX_TARGET_SPEED = 3.2
def get_target_data(context):
    # New Decision Maker
    tank = context.tank
    target = context.cur_target
    physics = context.physics

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

    allies_targeting = inverse_dict(context.memory.target_id, target.id)
    if len(allies_targeting) <= 1:
        estimate_pos = target_v + target_direction * ((target_avoid_distance_forward + target_avoid_distance_backward) / 2)
        vulnerable_width = max(90 * target_turret_n_cos, 60 * (1 - target_turret_n_cos))

        shoot = physics.will_hit(tank, fictive_unit(target, max_pos.x, max_pos.y), 0.9) and physics.will_hit(tank, fictive_unit(target, min_pos.x, min_pos.y), 0.9)

        return ((estimate_pos.x, estimate_pos.y), shoot, target_avoid_distance_forward, target_avoid_distance_backward, 'SINGLE')
    else:
        if context.memory.target_id[tank.id] != target.id:
            return None
        cnt = len(allies_targeting)
        ind = index_in_sorted(allies_targeting, tank.id)

        segment = (target_avoid_distance_forward - target_avoid_distance_backward)/(cnt + 1)

        shift = segment * (ind + 1) - target_avoid_distance_backward

        estimate_pos = target_v + target_direction * shift

        shoot = fabs(tank.get_turret_angle_to(estimate_pos.x, estimate_pos.y)) < PI/180 * 1
        return ((estimate_pos.x, estimate_pos.y), shoot, target_avoid_distance_forward, target_avoid_distance_backward, 'SEVERAL %d' % ind)

class ThirdRoundShootDecisionMaker(ShootDecisionMaker):
    def process(self, cur_target, move):
        tank = self.context.tank
        world = self.context.world
        memory = self.context.memory
        physics = self.context.physics

        self.physics = self.context.physics
        self.cur_target = cur_target
        self.world = self.context.world
        self.tank = self.context.tank
        self.memory = self.context.memory

        self.memory.target_id[tank.id] = cur_target.id
        est_pos, good_to_shoot = get_target_data(self)[:2]

        def bonus_is_attacked():
            for bonus in world.bonuses:
                if (self.physics.will_hit(tank, bonus, BONUS_FACTOR) and
                    tank.get_distance_to_unit(bonus) < tank.get_distance_to(*est_pos)):
                    return bonus
            return False

        def obstacle_is_attacked():
            obstacles = chain(
                filter(DEAD_TANK, world.tanks),
                filter(ALLY_TANK(tank.id), world.tanks),
                world.obstacles
            )
            for obstacle in obstacles:
                next_position = self.physics.estimate_target_position(obstacle, tank)
                next_unit = fictive_unit(obstacle, next_position[0], next_position[1])

                blocked = ((self.physics.will_hit(tank, next_unit, DEAD_TANK_OBSTACLE_FACTOR)
                            or self.physics.will_hit(tank, obstacle, DEAD_TANK_OBSTACLE_FACTOR))
                           and tank.get_distance_to_unit(obstacle) < tank.get_distance_to(*est_pos))
                if blocked:
                    return obstacle
            return False

        cur_angle = tank.get_turret_angle_to(*est_pos)

#        good_to_shoot = self.physics.will_hit(
#            tank,
#            fictive_unit(cur_target, est_pos[0], est_pos[1]),
#            0.5
#        )
        if good_to_shoot:
            if self.context.health_fraction > 0.8 and self.context.hull_fraction > 0.5 and tank.get_distance_to_unit(cur_target) > 400 and tank.premium_shell_count <= 3:
                move.fire_type = FireType.REGULAR
            else:
                move.fire_type = FireType.PREMIUM_PREFERRED
        else:
            move.fire_type = FireType.NONE

        if bonus_is_attacked() or obstacle_is_attacked():
            self.context.debug('!!! Obstacle is attacked, don\'t shoot')
            move.fire_type = FireType.NONE

        # Shoot bullets
        b = tank.angle + tank.turret_relative_angle
        for shell in world.shells:
            can_counter = fabs(PI - (shell.angle - b)) < PI/180 * 4
            if can_counter:
                can_counter = can_counter and physics.shell_will_hit(shell, tank) and shell.get_distance_to_unit(tank) < 100
            if can_counter:
                self.context.debug('!!! Possible to counter flying bullet')
                move.fire_type = FireType.REGULAR

        if fabs(cur_angle) > PI/180 * 0.5:
            move.turret_turn = cur_angle / PI * 180