from math import fabs, hypot
import operator
from GamePhysics import WorldPhysics
from Geometry import sign
from MyUtils import ALIVE_ENEMY_TANK, DEAD_TANK, ALLY_TANK, fictive_unit
from math import pi as PI
from itertools import chain
from model.FireType import FireType

# ================ CONSTANTS
# Targeting
TARGETING_FACTOR = 0.3
ENEMY_TARGETING_FACTOR = 0.8
BONUS_FACTOR = 1.25
DEAD_TANK_OBSTACLE_FACTOR = 1.15

# Memorizing stuff
VELOCITY_ESTIMATION_PERIOD = 3
VELOCITY_ESTIMATION_COUNT = 10

class OldTargetingStrategy:

    def __init__(self):
        pass

    def debug(self, message, end='\n',ticks_period=10):
        if self.world.tick % ticks_period == 0:
            if self.debug_mode:
                print(message,end=end)

    def change_state(self, tank, world, memory, debug_on):
        self.tank = tank
        self.world = world
        self.debug_mode = debug_on
        self.memory = memory

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
        process_shooting()


class EstimatorsTargetingStrategy:

    def __init__(self, target_estimators, decision_maker):
        self.target_estimators = target_estimators
        self.decision_maker = decision_maker

    def debug(self, message, end='\n',ticks_period=10):
        if self.world.tick % ticks_period == 0:
            if self.debug_mode:
                print(message,end=end)

    def change_state(self, tank, world, memory, debug_on):
        self.tank = tank
        self.world = world
        self.debug_mode = debug_on
        self.memory = memory

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

        targets = filter(ALIVE_ENEMY_TANK, world.tanks)

        if not targets:
            return

        for e in self.target_estimators:
            e.context = self


        if self.debug_mode:
            targets = sorted(targets, key=lambda t : t.player_name)
            self.debug(' ' * 60, end='')
            for e in self.target_estimators:
                self.debug('%14s' % e.NAME, end='')
            self.debug('%14s' % 'RESULT', end='')
            self.debug('')

            def out_tgt(tgt):
                def tgt_to_str(tgt):
                    return "TARGET [%12s] (x=%8.2f, y=%8.2f, |v|=%8.2f))" % (tgt.player_name, tgt.x, tgt.y, hypot(tgt.speedX, tgt.speedY))
                self.debug('%-60s' % (tgt_to_str(tgt) + ' : '), end='')
                res = 0
                for e in self.target_estimators:
                    if e.debugging:
                        v = e.debug_value(tgt)
                        self.debug('%14s' % str(v), end='')
                    else:
                        v = e.value(tgt)
                        self.debug('%14.2f' % v, end='')
                    #self.debug('%14.2f' % v, end='')

                    if not e.debugging:
                        res += v
                self.debug('%14.2f' % res, end='')
                self.debug('')

            for tgt in targets:
                out_tgt(tgt)

        get_target_priority = lambda target: sum([e.value(target) for e in self.target_estimators])

        targets_f = [(t, get_target_priority(t)) for t in targets]

        cur_target = max(targets_f, key=operator.itemgetter(1))[0]
        self.memory.last_turret_target_id = cur_target.id

        self.decision_maker.context = self
        self.decision_maker.process(cur_target, move)