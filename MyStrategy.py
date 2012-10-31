from model.FireType import FireType
from model.TankType import TankType
from model.BonusType import BonusType
from GamePhysics import *
from Geometry import sign
from math import pi as PI, sqrt
from model.Unit import Unit

# TODO:
#  * get rid of shaky behaviour (add previous target label?)
#  * ninja mode
#  * realistic moving and time estimation (we can do realistic estimation by ML)
#  * replace linear functions with desired
#  * position estimation by ML methods
#  * enemy distance estimation to bonus we're heading to
#  * take target orientation into account when shooting
#  * Additional tactical positions

DEBUG_MODE = True

# ================ CONSTANTS
TARGETING_FACTOR = 0.6
ENEMY_TARGETING_FACTOR = 0.8
BONUS_FACTOR = 1.25

ALIVE_ENEMY_TANK = lambda t: not t.teammate and t.crew_health > 0 and t.hull_durability > 0
DEAD_TANK = lambda t: t.crew_health == 0 or t.hull_durability == 0

UNIT_TO_POINT = lambda unit: (unit.x, unit.y)

def fictive_unit(prototype, x, y):
    return Unit(0, prototype.width, prototype.height, x, y, 0, 0, prototype.angle, 0)

def closest_to(coord):
    return lambda arg: min(arg, key=lambda item: distance(item, coord))

def unit_closest_to(x, y):
    return lambda arg: min(arg, key=lambda item: item.get_distance_to(x, y))

class MyStrategy:

    class Memory:
        pass

    def debug(self, message, ticks_period=20):
        if self.world.tick % ticks_period == 0:
            if DEBUG_MODE:
                print(message)

    def move(self, tank, world, move):
        self.world = world

        def process_moving():
            positions = []
            # Screen corners
            for i in range(3):
                for j in range(3):
                    positions.append((world.width * (1 + 2*i) / 6, world.height * (1 + 2*j) / 6))

            # Grid
#            GRID_HOR_COUNT = 15
#            GRID_VERT_COUNT = 10
#            for i in range(GRID_HOR_COUNT):
#                for j in range(GRID_VERT_COUNT):
#                    positions.append((world.width * (1 + i) / (GRID_HOR_COUNT + 1),
#                                      world.height * (1 + j) / (GRID_VERT_COUNT + 1)))

            # Forward and backward direction

            # Bonuses positions
            positions += [(b.x, b.y) for b in world.bonuses]

            if not positions:
                return

            def estimate_position_F(x, y):
                est_time = estimate_time_to_position(x, y, tank)
                enemies = list(filter(ALIVE_ENEMY_TANK, world.tanks))
                health_fraction = tank.crew_health / tank.crew_max_health
                hull_fraction = tank.hull_durability / tank.hull_max_durability

                # Bonus priority:
                # + Need this bonus
                # (*) - Close to enemy going for it

                try:
                    closest_bonus = unit_closest_to(x, y)(world.bonuses)

                    if closest_bonus.type == BonusType.MEDIKIT:
                        bonus_profit = 200 + (1 - health_fraction) * 1300
                    elif closest_bonus.type == BonusType.REPAIR_KIT:
                        bonus_profit = 100 + (1 - hull_fraction) * 900
                    elif closest_bonus.type == BonusType.AMMO_CRATE:
                        bonus_profit = 400
                    else:
                        bonus_profit = 0

                    try:
                        enemy_closest_to_bonus = min(enemies, key=lambda t: estimate_time_to_position(x, y, t))
                        bonus_enemy = max(0, (est_time - estimate_time_to_position(x, y, enemy_closest_to_bonus)) * 0.7)
                    except Exception as e:
                        self.debug("$$$ This is highly unexpected %s" % e)

                        bonus_enemy = 0
                    # TODO: fix and then return back
                    bonus_enemy = 0

                    bonus_summand = max(0, bonus_profit - bonus_enemy)

                    if closest_bonus.get_distance_to(x, y) > 10:
                        bonus_summand = 0
                except:
                    bonus_summand = 0

                # How dangerous position is
                # + In centre of massacre
                # + Flying shells
                # + Turrets directed
                try:
                    enemies_count = len(enemies)
                    danger_penalty = -sum(map(lambda enemy: enemy.get_distance_to(x, y), enemies)) / (enemies_count)
                except:
                    danger_penalty = 0
                danger_penalty += 1200

                if len(enemies) > 3 or health_fraction < 0.7 or hull_fraction < 0.6:
                    danger_penalty_factor = 1
                elif len(enemies) == 1 and health_fraction > 0.7 and hull_fraction > 0.5:
                    danger_penalty_factor = 0.2
                else:
                    danger_penalty_factor = 0.8
                danger_penalty *= danger_penalty_factor

                #observed_by_enemy = 0
                #for enemy in enemies:
                #    if will_hit(enemy, tank, ENEMY_TARGETING_FACTOR):
                #        observed_by_enemy += 1
                stopping_penalty = 0
                if bonus_summand == 0:
                    stopping_penalty = 2 * max(0, 400 - tank.get_distance_to(x, y))

                # Position priority:
                # + Bonus priority
                # - Dangerous position
                # - Close to screen edges (*)
                # - Don't stay at one place (*)
                est_time *= 0.6
                result = 2000 + bonus_summand - est_time - stopping_penalty - danger_penalty
                self.debug(('Position: x=%8.2f, y=%8.2f, bonus_summand=%8.2f, est_time=%8.2f, ' +
                            'stopping_penalty=%8.2f, danger_penalty=%8.2f, result=%8.2f') %
                            (x, y, bonus_summand, est_time, stopping_penalty, danger_penalty, result))
                return result

            next_position = max(positions, key=lambda x_y: estimate_position_F(x_y[0], x_y[1]))
            move_to_position(next_position[0], next_position[1], tank, move)

        def process_shooting():
            targets = filter(ALIVE_ENEMY_TANK, world.tanks)

            if not targets:
                return

            def get_target_priority(tank, target):
                result = -tank.get_distance_to_unit(target) / 50 - tank.get_turret_angle_to_unit(target)
                # Headshot ^_^
                if ((target.crew_health <= 20 or target.hull_durability <= 20) or
                    (tank.premium_shell_count > 0 and (target.crew_health < 35 or target.hull_durability <= 35))):
                    result += 15
                return result

            cur_target = max(targets, key=lambda t: get_target_priority(tank, t))
            est_pos = estimate_target_position(cur_target, tank)

            def bonus_attacked():
                for bonus in world.bonuses:
                    if (will_hit(tank, bonus, BONUS_FACTOR) and
                       tank.get_distance_to_unit(bonus) < tank.get_distance_to(*est_pos)):
                        return bonus
                return False

            def dead_tank_attacked():
                for obstacle in filter(DEAD_TANK, world.tanks):
                    if (will_hit(tank, obstacle, BONUS_FACTOR) and
                        tank.get_distance_to_unit(obstacle) < tank.get_distance_to(*est_pos)):
                        return obstacle
                return False

            cur_angle = tank.get_turret_angle_to(*est_pos)
            if will_hit(
                tank,
                fictive_unit(cur_target, est_pos[0], est_pos[1]),
                TARGETING_FACTOR
            ):
                move.fire_type = FireType.PREMIUM_PREFERRED
            else:
                move.fire_type = FireType.NONE

            if bonus_attacked() or dead_tank_attacked():
                self.debug('!!! Obstacle is attacked, don\'t shoot')
                move.fire_type = FireType.NONE

            if fabs(cur_angle) > PI/180 * 0.5:
                move.turret_turn = sign(cur_angle)

        self.debug('========================= (Tick) #%s =====================' % world.tick)
        self.debug('Tank (x=%s, y=%s, health=%4s/%4s, super_shells=%2s)' %
                   (tank.x, tank.y, tank.crew_health, tank.crew_max_health, tank.premium_shell_count))

        process_moving()
        process_shooting()

        self.debug('Output: left: %5.2f, right: %5.2f' % (move.left_track_power, move.right_track_power))

    def select_tank(self, tank_index, team_size):
        return TankType.MEDIUM