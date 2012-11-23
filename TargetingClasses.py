from itertools import chain
from math import fabs, cos
from GamePhysics import INITIAL_SHELL_VELOCITY, SHELL_ACCELERATION
from Geometry import sign, Vector, get_unit_corners
from MyUtils import DEAD_TANK, ALLY_TANK, fictive_unit, solve_quadratic, inverse_dict, index_in_sorted, debug_dump, TANK
from model.FireType import FireType
from math import pi as PI

class ShootDecisionMaker:
    context = None

DEBUG_VIS = False

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
MAX_TARGET_SPEED = 2.5
BACKWARDS_FICTIVE_MULTIPLIER = 0.9
def get_target_data(context):
    # New Decision Maker
    tank = context.tank
    target = context.cur_target
    physics = context.physics

    b = tank.angle + tank.turret_relative_angle
    #e = Vector(1, 0)
    #q = e.rotate(b)
    tank_v = Vector(tank.x, tank.y)

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
    #center = Vector(target.x - tank.x, target.y - tank.y)

    v0 = target_speed.projection(target_direction)
    target_health_fraction = target.crew_health/target.crew_max_health
    efficency = (1 + target_health_fraction)/2

    target_avoid_distance_forward = max_move_distance(v0, FICTIVE_TARGET_ACCELERATION * efficency, MAX_TARGET_SPEED * efficency, t)
    target_avoid_distance_backward = max_move_distance(v0, -FICTIVE_TARGET_ACCELERATION * BACKWARDS_FICTIVE_MULTIPLIER * efficency, MAX_TARGET_SPEED * efficency, t)
    max_pos = target_v + target_avoid_distance_forward * target_direction
    min_pos = target_v + target_avoid_distance_backward * target_direction

    target_turret_n_cos = fabs(cos(fabs(b - target.angle) + PI/2))

    var = fabs((target_avoid_distance_forward - target_avoid_distance_backward) * target_turret_n_cos)

    allies_targeting = inverse_dict(context.memory.target_id, target.id)

    def single_attacker():
        #estimate_pos = target_v + target_direction * ((target_avoid_distance_forward + target_avoid_distance_backward) / 2)
        vulnerable_width = max(90 * target_turret_n_cos, 60 * (1 - target_turret_n_cos))

        max_pos_fu = fictive_unit(target, max_pos.x, max_pos.y)
        min_pos_fu = fictive_unit(target, min_pos.x, min_pos.y)

        #shoot = physics.will_hit(tank, max_pos_fu, 0.9) and physics.will_hit(tank, min_pos_fu, 0.9)

        shoot_precise = physics.will_hit_precise(tank, max_pos_fu) and physics.will_hit_precise(tank, min_pos_fu) and physics.will_hit_precise(tank, target)
        shoot = shoot_precise
        fabs(target_turret_n_cos)

        all_corners = get_unit_corners(max_pos_fu) + get_unit_corners(min_pos_fu)
        #closest_corner = min(all_corners, key=lambda c: c.distance(tank_v))
        # Instead of closest corner try to target middle of colsest side
        sc1, sc2 = sorted(all_corners, key=lambda c: c.distance(tank_v))[:2]
        closest_corner = 0.75 * sc1 + 0.25 * sc2

        middle_position = (max_pos + min_pos)/2

        w = fabs(target_turret_n_cos)**2
        estimate_pos = w*middle_position + (1 - w) * closest_corner

        comment = 'SINGLE, %s' % w

        if obstacle_is_attacked(context, estimate_pos):
            shoot = False
            comment += ' blocked'

        if DEBUG_VIS:
            if shoot and tank.remaining_reloading_time == 0:
                debug_data = {
                    "units": [min_pos_fu, max_pos_fu, target],
                    "tanks": [tank]
                }
                debug_dump(debug_data, "/".join([str(context.memory.battle_id), str(context.world.tick) + "_" + str(tank.id) + "_single"]))

        return ((estimate_pos.x, estimate_pos.y), shoot, target_avoid_distance_forward, target_avoid_distance_backward, comment)

    def multiple_attackers(attackers):
        cnt = len(allies_targeting)
        ind = index_in_sorted(allies_targeting, tank.id)

        segment = (target_avoid_distance_forward - target_avoid_distance_backward)/(cnt + 1)

        shift = segment * (ind + 1) + target_avoid_distance_backward
        #shift *
        if cnt == 2:
            if ind == 0:
                shift = target_avoid_distance_backward + 80
            else:
                shift = target_avoid_distance_forward - 80

        estimate_pos = target_v + target_direction * shift
        shift_fu = fictive_unit(target, estimate_pos.x, estimate_pos.y)

        shoot = (physics.will_hit_precise(tank, shift_fu) and
                 all([lambda a: a.remaining_reloading_time < 5 or a.reloading_time - a.remaining_reloading_time < 5, attackers]))

        comment = 'MULTIPLE(%d), shift=%8.2f' % (ind, shift)
        if obstacle_is_attacked(context, estimate_pos):
            shoot = False
            comment += ' blocked'

        if DEBUG_VIS:
            if shoot and tank.remaining_reloading_time == 0 and all([context.memory.good_to_shoot.get(t.id) or t.id == tank.id for t in attackers]):
                max_pos_fu = fictive_unit(target, max_pos.x, max_pos.y)
                min_pos_fu = fictive_unit(target, min_pos.x, min_pos.y)
                debug_data = {
                    "units": [min_pos_fu, max_pos_fu, target],
                    "tanks": attackers
                }
                debug_dump(debug_data, "/".join([str(context.memory.battle_id), str(context.world.tick) + "_" + str(tank.id) + "_multiple"]))

        return ((estimate_pos.x, estimate_pos.y), shoot, target_avoid_distance_forward, target_avoid_distance_backward, comment)

    context.memory.good_to_shoot[tank.id] = False

    try_single = single_attacker()
    if len(allies_targeting) > 1 and try_single[1] == False:

        if tank.id in allies_targeting:
            attackers = []
            for t in context.world.tanks:
                if t.id in allies_targeting:
                    attackers.append(t)
            if all([lambda a: a.remaining_reloading_time < 70 or a.reloading_time - a.remaining_reloading_time < 5, attackers]):
                try_multiple = multiple_attackers(attackers)
                if try_multiple[1]:
                    context.memory.good_to_shoot[tank.id] = True
                    ok = all([context.memory.good_to_shoot.get(t.id) for t in attackers])
                    if not ok:
                        try_multiple = (try_multiple[0], False)

                return try_multiple
    return try_single


def obstacle_is_attacked(context, est_pos):
    world = context.world
    tank = context.tank
    physics = context.physics

    obstacles = chain(
        filter(DEAD_TANK, world.tanks),
        filter(ALLY_TANK(tank.id), world.tanks)
    )
    for obstacle in obstacles:
        next_position = physics.estimate_target_position(obstacle, tank)
        next_unit = fictive_unit(obstacle, next_position[0], next_position[1])

        blocked = ((physics.will_hit(tank, next_unit, DEAD_TANK_OBSTACLE_FACTOR)
                    or physics.will_hit(tank, obstacle, DEAD_TANK_OBSTACLE_FACTOR))
                   and tank.get_distance_to_unit(obstacle) < tank.get_distance_to(est_pos.x, est_pos.y))
        if blocked:
            return obstacle

    for bonus in world.bonuses:
        if (physics.will_hit(tank, bonus, BONUS_FACTOR) and
            tank.get_distance_to_unit(bonus) < tank.get_distance_to(est_pos.x, est_pos.y)):
            return bonus

    bunker_obstacle = world.obstacles[0]
    if (physics.will_hit(tank, bunker_obstacle, 1.04) and
        tank.get_distance_to_unit(bunker_obstacle) < tank.get_distance_to(est_pos.x, est_pos.y)):
        return bunker_obstacle
    return False

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

        cur_angle = tank.get_turret_angle_to(*est_pos)

        if good_to_shoot:
            if self.context.health_fraction > 0.8 and self.context.hull_fraction > 0.5 and tank.get_distance_to_unit(cur_target) > 400 and tank.premium_shell_count <= 3:
                move.fire_type = FireType.REGULAR
            else:
                move.fire_type = FireType.PREMIUM_PREFERRED
        else:
            move.fire_type = FireType.NONE

        # Shoot bullets
        def process_bullets():
            b = tank.angle + tank.turret_relative_angle
            for shell in world.shells:
                can_counter = fabs(PI - (shell.angle - b)) < PI/180 * 4
                if can_counter:
                    can_counter = can_counter and physics.shell_will_hit(shell, tank) and shell.get_distance_to_unit(tank) < 100
                if can_counter:
                    self.context.debug('{Shooting} Possible to counter flying bullet')
                    move.fire_type = FireType.REGULAR

        #process_bullets()

        if fabs(cur_angle) > PI/180 * 0.5:
            move.turret_turn = cur_angle / PI * 180