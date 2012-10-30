from model.FireType import FireType
from model.TankType import TankType
from model.BonusType import BonusType
from GamePhysics import *
from Geometry import sign
from math import pi as PI, sqrt

# TODO:
#  * realistic obstacle hitting
#  * get rid of shaky behaviour
from model.Unit import Unit

DEBUG_MODE = True

# ================ CONSTANTS
TARGETING_FACTOR = 0.6
BONUS_FACTOR = 1.25

ALIVE_ENEMY_TANK = lambda t: not t.teammate and t.crew_health > 0 and t.hull_durability > 0

UNIT_TO_POINT = lambda unit: (unit.x, unit.y)

def closest_to(coord):
    return lambda arg: min(arg, key=lambda item: distance(item, coord))

def unit_closest_to(x, y):
    return lambda arg: min(arg, key=lambda item: item.get_distance_to(x, y))

class MyStrategy:

    def debug(self, message, ticks_period=20):
        if self.world.tick % ticks_period == 0:
            if DEBUG_MODE:
                print(message)

    def move(self, tank, world, move):
        self.world = world

        def process_moving():
            # TODO:
            # * Add tactical positions
            positions = []
            # Screen corners
            for i in range(3):
                for j in range(3):
                    positions.append((world.width * (1 + 2*i) / 6, world.height * (1 + 2*j) / 6))

            # Forward and backward direction

            # Bonuses positions
            positions += [(b.x, b.y) for b in world.bonuses]

            if not positions:
                return

            def estimate_position_F(x, y):
                est_time = estimate_time_to_position(x, y, tank)

                # Bonus priority:
                # + Need this bonus
                # - Close to enemy
                # - Flying shells
                # - Turrets directed
                #
                # TODO:
                # * enemy distance estimation
                # * smarter priorities
                # * ninja mode
                try:
                    closest_bonus = unit_closest_to(x, y)(world.bonuses)

                    if closest_bonus.type == BonusType.MEDIKIT:
                        health_fraction = tank.crew_health / tank.crew_max_health
                        bonus_profit = 200 + (1 - health_fraction) * 1300
                    elif closest_bonus.type == BonusType.REPAIR_KIT:
                        hull_fraction = tank.hull_durability / tank.hull_max_durability
                        bonus_profit = 100 + (1 - hull_fraction) * 900
                    elif closest_bonus.type == BonusType.AMMO_CRATE:
                        bonus_profit = 400
                    else:
                        bonus_profit = 0

                    bonus_enemy = 0

                    bonus_summand = max(0, bonus_profit - bonus_enemy)

                    if closest_bonus.get_distance_to(x, y) > 10:
                        bonus_summand = 0
                except:
                    bonus_summand = 0

                # How dangerous position is
                try:
                    enemies = list(filter(ALIVE_ENEMY_TANK, world.tanks))
                    enemies_count = len(enemies)
                    danger_penalty = -sum(map(lambda enemy: enemy.get_distance_to(x, y), enemies)) / (enemies_count)
                except:
                    danger_penalty = 0
                danger_penalty += 1200
                # Position priority:
                # + Bonus priority
                # - Dangerous position
                # - Close to screen edges
                # - Don't stay at one place
                # + Tactical advantage (?)

                stopping_penalty = 0
                if bonus_summand == 0:
                    stopping_penalty = max(0, 400 - tank.get_distance_to(x, y))
                stopping_penalty *= 0

                result = 2000 + bonus_summand - est_time - stopping_penalty - danger_penalty
                self.debug('Position: x=%8.2f, y=%8.2f, bonus_summand=%8.2f, est_time=%8.2f, stopping_penalty=%8.2f, danger_penalty=%8.2f, result=%8.2f' %
                           (x, y, bonus_summand, est_time, stopping_penalty, danger_penalty, result))
                return result

            #self.debug('\n'.join(['Position (%s, %s, %s)' % item for item in [(x_y[0], x_y[1], estimate_position_F(x_y[0], x_y[1])) for x_y in positions]]))

            next_position = max(positions, key=lambda x_y: estimate_position_F(x_y[0], x_y[1]))
            move_to_position(next_position[0], next_position[1], tank, move)

        def process_shooting():
            # TODO:
            #  + targeting in advance
            #  * take target orientation into account
            #  + don't shoot bonuses
            targets = filter(ALIVE_ENEMY_TANK, world.tanks)

            if not targets:
                return

            def get_target_priority(tank, target):
                result = -tank.get_distance_to_unit(target) / 60 - tank.get_turret_angle_to_unit(target)
                # Headshot ^_^
                if ((target.crew_health <= 20 or target.hull_durability <= 20) or
                    (tank.premium_shell_count > 0 and (target.crew_health < 35 or target.hull_durability <= 35))):
                    result += 15
                return result

            cur_target = max(targets, key=lambda t: get_target_priority(tank, t))
            est_pos = estimate_target_position(cur_target, tank)

            def bonus_attacked():
                for bonus in world.bonuses:
                    if (will_hit(tank, bonus, BONUS_FACTOR) and \
                       tank.get_distance_to_unit(bonus) < tank.get_distance_to(*est_pos)):
                        return bonus
                return False

            cur_angle = tank.get_turret_angle_to(*est_pos)
            if will_hit(
                tank,
                Unit(0, cur_target.width, cur_target.height, est_pos[0], est_pos[1], 0, 0, cur_target.angle, 0),
                TARGETING_FACTOR
            ):
                move.fire_type = FireType.PREMIUM_PREFERRED
            else:
                move.fire_type = FireType.NONE

            if bonus_attacked():
                q = bonus_attacked()
                self.debug('!!! Bonus is attacked (%8.2f, %8.2f)' % (q.x, q.y), 1)
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