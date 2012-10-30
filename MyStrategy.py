from model.FireType import FireType
from model.TankType import TankType
from GameGeometry import *
from math import pi as PI, copysign

def sign(x):
    return copysign(1, x)

class MyStrategy:

    def debug(self, message, ticks_period=50):
        if self.world.tick % ticks_period == 0:
            print(message)

    def move(self, tank, world, move):
        self.world = world

        def process_moving():
            positions = []
            positions += [(b.x, b.y) for b in world.bonuses]

            if not positions:
                return

            def estimate_position_F(x, y):
                return - estimate_time_to_position(x, y, tank)

            self.debug('=========================')
            self.debug('Tank (x=%s, y=%s)' % (tank.x, tank.y))
            self.debug('\n'.join(['Position (%s, %s, %s)' % item for item in [(x_y[0], x_y[1], estimate_position_F(x_y[0], x_y[1])) for x_y in positions]]))

            next_position = max(positions, key=lambda x_y: estimate_position_F(x_y[0], x_y[1]))
            move_to_position(next_position[0], next_position[1], tank, move)

        def process_shooting():
            # TODO:
            # targeting in advance
            # take target orientation into account
            good_target = lambda t: not t.teammate and t.crew_health > 0 and t.hull_durability > 0
            targets = filter(good_target, world.tanks)

            if not targets:
                return

            def get_target_priority(tank, target):
                return -tank.get_distance_to_unit(target) / 40 - tank.get_turret_angle_to_unit(target)

            cur_target = max(targets, key=lambda t: get_target_priority(tank, t))

            cur_angle = tank.get_turret_angle_to_unit(cur_target)
            if fabs(cur_angle) < PI/180 * 5 and tank.get_distance_to_unit(cur_target) < 200:
                move.fire_type = FireType.PREMIUM_PREFERRED
            elif fabs(cur_angle) < PI/180 * 20 and tank.get_distance_to_unit(cur_target) < 120:
                move.fire_type = FireType.PREMIUM_PREFERRED
            elif fabs(cur_angle) < PI/180 * 1:
                move.fire_type = FireType.PREMIUM_PREFERRED
            else:
                move.fire_type = FireType.NONE

            if fabs(cur_angle) > PI/180 * 0.5:
                move.turret_turn = sign(cur_angle)

        process_moving()
        process_shooting()

    def select_tank(self, tank_index, team_size):
        return TankType.MEDIUM