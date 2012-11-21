from itertools import chain
from math import fabs
from Geometry import sign
from MyUtils import DEAD_TANK, ALLY_TANK, fictive_unit
from model.FireType import FireType
from math import pi as PI

class ShootDecisionMaker:
    context = None

# ================ CONSTANTS
# Targeting
TARGETING_FACTOR = 0.3
ENEMY_TARGETING_FACTOR = 0.8
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

class ThirdRoundShootDecisionMaker(ShootDecisionMaker):
    def process(self, cur_target, move):
        tank = self.context.tank
        world = self.context.world
        memory = self.context.memory

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
            0.6
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

#        if tank.remaining_reloading_time == 0 and move.fire_type != FireType.NONE:
#            if memory.last_shot_tick is None or memory.last_shot_tick < world.tick - 2:
#                memory.last_shot_tick = world.tick
#            else:
#                move.fire_type = FireType.NONE

        if fabs(cur_angle) > PI/180 * 0.5:
            move.turret_turn = sign(cur_angle)