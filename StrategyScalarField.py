from math import fabs, hypot
from queue import PriorityQueue
import operator
from random import random
from GamePhysics import WorldPhysics
from Geometry import sign
from MyUtils import ALIVE_ENEMY_TANK, filter_or, DEAD_TANK, ALLY_TANK, fictive_unit
from math import pi as PI
from itertools import chain

# ================ CONSTANTS
# Moving
from model.FireType import FireType

MAX_POSITION_ITERATIONS = 10

# Targeting
TARGETING_FACTOR = 0.3
ENEMY_TARGETING_FACTOR = 0.8
BONUS_FACTOR = 1.25
DEAD_TANK_OBSTACLE_FACTOR = 1.15

# Memorizing stuff
VELOCITY_ESTIMATION_PERIOD = 3
VELOCITY_ESTIMATION_COUNT = 10
class StrategyScalarField:
    def __init__(self, tank, world, position_getters, position_estimators, memory, debug_on=False):
        self.tank = tank
        self.world = world
        self.debug_mode = debug_on
        self.position_getters = position_getters
        self.position_estimators = position_estimators
        self.memory = memory

        self.physics = WorldPhysics(world)

    def debug(self, message, end='\n',ticks_period=10):
        if self.world.tick % ticks_period == 0:
            if self.debug_mode:
                print(message,end=end)

    def change_state(self, tank, world):
        self.tank = tank
        self.world = world

        self.physics = WorldPhysics(world)

    def make_turn(self, move):
        return self._make_turn(self.tank, self.world, move)

    def _make_turn(self, tank, world, move):
        # Precalc for estimation
        self.enemies = list(filter(ALIVE_ENEMY_TANK, world.tanks))
        self.allies = list(filter(ALLY_TANK(tank.id), world.tanks))
        self.health_fraction = tank.crew_health / tank.crew_max_health
        self.hull_fraction = tank.hull_durability / tank.hull_max_durability
        self.enemies_count = len(self.enemies)
        self.EA_cache = {}
        self.est_time_cache = {}

        def process_moving():
            positions = []
            for pg in self.position_getters:
                positions += pg.positions(tank, world)
            self.debug('Got %d positions' % len(positions))
            if not positions:
                return

            for e in self.position_estimators:
                e.context = self
            pos_and_values = [(pos, sum([e.value(pos) for e in self.position_estimators]))
                              for pos in positions]

            if self.debug_mode:
                top_pos = [item[0] for item in list(reversed(sorted(pos_and_values, key=operator.itemgetter(1))))[:6]]

                self.debug(' ' * 50, end='')
                for e in self.position_estimators:
                    self.debug('%14s' % e.NAME, end='')
                self.debug('%14s' % 'RESULT', end='')
                self.debug('')

                def out_pos(pos):
                    self.debug('%-50s' % (str(pos) + ' : '), end='')
                    res = 0
                    for e in self.position_estimators:
                        v = e.value(pos)
                        self.debug('%14.2f' % v, end='')
                        res += v
                    self.debug('%14.2f' % res, end='')
                    self.debug('')

                for pos in top_pos:
                    out_pos(pos)
                self.debug('=' * 16)
                for pos in positions:
                    if pos.name.find('BONUS') != -1:
                        out_pos(pos)
                self.debug('=' * 16)
                for pos in positions:
                    if pos.name == 'FORWARD' or pos.name == 'BACKWARD' or pos.name == 'CURRENT':
                        out_pos(pos)

                self.debug('=' * 16)
                for pos in positions:
                    if pos.name.find('BORDER') != -1:
                        out_pos(pos)


            next_position = None

            position_iteration = 0
            #average_F = sum([pos[0] for pos in pos_f])/len(pos_f)
            pos_queue = PriorityQueue()
            for p_v in pos_and_values:
                pos_queue.put( (-p_v[1] + random() * 1e-3, p_v[0]) )

            while True:
                cur = pos_queue.get()[1]
                if not self.physics.position_is_blocked(cur.x, cur.y, tank, world) or position_iteration >= MAX_POSITION_ITERATIONS:
                    next_position = cur
                    break
                position_iteration += 1
                self.debug('!!! Skipping best position, iteration %d' % position_iteration)
                if self.debug_mode:
                    self.debug('(blocked by %s)' % str(self.physics.position_is_blocked(cur.x, cur.y, tank, world)))

            self.debug("GOING TO [%10s] (%8.2f, %8.2f); distance=%8.2f, ETA=%8.2f" %
                       (next_position.name, next_position.x, next_position.y,
                        self.tank.get_distance_to(next_position.x, next_position.y), self.physics.estimate_time_to_position(next_position.x, next_position.y, tank))
            )
            self.memory.last_target_position[tank.id] = next_position
            self.physics.move_to_position(next_position.x, next_position.y, tank, move)

        def process_shooting():
            targets = filter(ALIVE_ENEMY_TANK, world.tanks)

            if not targets:
                return

            def get_target_priority(tank, target):
                health_fraction = tank.crew_health / tank.crew_max_health

                # ================
                # DISTANCE
                # ================
                angle_penalty_factor = (1 + (1 - health_fraction) * 1.5 -
                                        (1 - max(0, 150 - tank.remaining_reloading_time)/150) * 1)

                angle_degrees = fabs(tank.get_turret_angle_to_unit(target)) / PI * 180

                distance_penalty = tank.get_distance_to_unit(target) / 10
                angle_penalty = angle_penalty_factor * (angle_degrees**1.2)/2

                # ================
                # FINISH
                # ================
                if ((target.crew_health <= 20 or target.hull_durability <= 20) or
                    (tank.premium_shell_count > 0 and (target.crew_health <= 35 or target.hull_durability <= 35))):
                    finish_bonus = 30
                else:
                    finish_bonus = 0

                # ================
                # RESPONSE
                # ================
                if self.physics.attacked_area(tank.x, tank.y, target, cache=self.EA_cache) > 0.5:
                    attacking_me_bonus = 20
                else:
                    attacking_me_bonus = 0

                # ================
                # LAST TARGET
                # ================
                last_target_bonus = 0
                if self.memory.last_turret_target_id:
                    if self.memory.last_turret_target_id == target.id:
                        last_target_bonus = 5

                result = 180 + finish_bonus + attacking_me_bonus + last_target_bonus - distance_penalty - angle_penalty
                self.debug('TARGET [%20s] (x=%8.2f, y=%8.2f, |v|=%8.2f) finish_B=%8.2f, AM_B=%8.2f, LT_B=%8.2f, D_P=%8.2f, A_P=%8.2f, APF=%8.2f, result=%8.2f' %
                           (target.player_name, target.x, target.y, hypot(target.speedX, target.speedY), finish_bonus, attacking_me_bonus, last_target_bonus,
                            distance_penalty, angle_penalty, angle_penalty_factor, result))
                return result

            if self.debug_mode:
                targets = sorted(targets, key=lambda t : t.player_name)
            targets_f = [(t, get_target_priority(tank, t)) for t in targets]

            cur_target = max(targets_f, key=operator.itemgetter(1))[0]
            self.memory.last_turret_target_id = cur_target.id

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
                if self.health_fraction > 0.8 and self.hull_fraction > 0.5 and tank.get_distance_to_unit(cur_target) > 400 and tank.premium_shell_count <= 3:
                    move.fire_type = FireType.REGULAR
                else:
                    move.fire_type = FireType.PREMIUM_PREFERRED
            else:
                move.fire_type = FireType.NONE

            if bonus_is_attacked() or obstacle_is_attacked():
                self.debug('!!! Obstacle is attacked, don\'t shoot')
                move.fire_type = FireType.NONE

            if world.tick < 10 + tank.teammate_index * 10:
                move.fire_type = FireType.NONE

            if fabs(cur_angle) > PI/180 * 0.5:
                move.turret_turn = sign(cur_angle)

        process_moving()
        self.debug('=' * 16)
        process_shooting()