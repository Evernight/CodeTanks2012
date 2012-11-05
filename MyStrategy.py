import operator
from model.FireType import FireType
from model.TankType import TankType
from model.BonusType import BonusType
from GamePhysics import *
from Geometry import sign
from math import pi as PI
from collections import deque, defaultdict
from MyUtils import *
import pickle

# TODO:
#  * don't push enemies to bonuses
#  * get rid of shaky behaviour (add previous target label?)
#  * ninja mode (take into account flying shells and directed turrets)
#  * realistic moving and time estimation (we can do realistic estimation by ML)
#  * replace linear functions with desired
#  * position estimation by ML methods
#  * enemy distance estimation to bonus we're heading to
#  * estimate ability to predict target position
#  * Additional tactical positions
#  * take target orientation into account when shooting
#  * possible to change targets but shoot anyway
#  * when targeting take current moving destination into account (or the opposite)
#  * standing death?
#  * pick very close bonuses, don't go straightforward to better ones

DEBUG_MODE = False
PHYSICS_RESEARCH_MODE = False

# ================ CONSTANTS
# Targeting
TARGETING_FACTOR = 0.6
ENEMY_TARGETING_FACTOR = 0.8
BONUS_FACTOR = 1.25
DEAD_TANK_OBSTACLE_FACTOR = 1.05

# Memorizing stuff
VELOCITY_ESTIMATION_PERIOD = 3
VELOCITY_ESTIMATION_COUNT = 10

# Phys analysis
ANALYSIS_TARGET_SAVE_DISTANCE = 80

# Utils
class MyStrategy:

    class Memory:
        def __init__(self):
            self.velocity_history = defaultdict(deque)
            self.last_target_position = None
            self.last_target_time = 0
            self.last_turret_target_id = None

    class PhysicsAnalyser:
        def __init__(self):
            self.shell_velocity = defaultdict(list)
            self.last_target_time_init_values = None
            self.targets = []

        def store_shell_velocity(self, world):
            if not PHYSICS_RESEARCH_MODE:
                return
            for shell in world.shells:
                self.shell_velocity[shell.id].append(Vector(shell.speedX, shell.speedY).length())
            if world.tick % 100 == 0:
                pickle.dump(self.shell_velocity, open('shells.dump', 'wb'))

        def save_target_init_values(self, tank, x, y):
            if not PHYSICS_RESEARCH_MODE:
                return

            dist = tank.get_distance_to(x, y)
            vt = Vector(tank.speedX, tank.speedY)

            tank_v = Vector(tank.x, tank.y)
            pt_v = Vector(x, y)
            d = pt_v - tank_v

            tank_d_v = Vector(1, 0).rotate(tank.angle)

            if vt.is_zero():
                vd_angle = 0
            else:
                vd_angle = vt.angle(d)

            if d.is_zero():
                self.last_target_time_init_values = (0, 0, 0, 0, 0, 0)

            self.last_target_time_init_values = (
                tank_d_v.angle(d),
                dist,
                vd_angle,
                vt.length(),
                tank.angular_speed,
                tank.crew_health/tank.crew_max_health
            )

        def store_target_reached(self, world, time):
            if not PHYSICS_RESEARCH_MODE:
                return
            self.targets.append(self.last_target_time_init_values + (time, ))

            try:
                with open('targets.dump', 'rb') as f:
                    tmp = pickle.load(f)
            except:
                tmp = []
            with open('targets.dump', 'wb') as f:
                #pickle.dump(tmp + self.targets, f)
                pickle.dump(tmp + [self.last_target_time_init_values + (time, )], f)


    def __init__(self):
        self.memory = MyStrategy.Memory()
        self.analysis = MyStrategy.PhysicsAnalyser()

    def debug(self, message, ticks_period=5):
        if self.world.tick % ticks_period == 0:
            if DEBUG_MODE:
                print(message)

    def move(self, tank, world, move):
        self.world = world

        def process_moving():
            positions = []

            # Grid
            GRID_HOR_COUNT = 10
            GRID_VERT_COUNT = 7
            for i in range(GRID_HOR_COUNT):
                for j in range(GRID_VERT_COUNT):
                    positions.append((world.width * (1 + i) / (GRID_HOR_COUNT + 1),
                                      world.height * (1 + j) / (GRID_VERT_COUNT + 1), "GRID %s, %s" % (i, j)))

            # Forward and back direction
            tank_v = Vector(tank.x, tank.y)
            tank_d_v = Vector(1, 0).rotate(tank.angle)
            forw = tank_v + tank_d_v * 80
            back = tank_v - tank_d_v * 80
            positions.append((forw.x, forw.y, "FORWARD"))
            positions.append((back.x, back.y, "BACKWARD"))

            # Bonuses positions
            positions += [(b.x, b.y, "BONUS %s" % bonus_name_by_type(b.type)) for b in world.bonuses]

            if not positions:
                return

            # Precalc for estimation
            enemies = list(filter(ALIVE_ENEMY_TANK, world.tanks))
            health_fraction = tank.crew_health / tank.crew_max_health
            hull_fraction = tank.hull_durability / tank.hull_max_durability
            enemies_count = len(enemies)

            def estimate_position_F(x, y, name="?", show_debug=False):
                est_time = estimate_time_to_position(x, y, tank)

                # Bonus priority:
                # + Need this bonus
                # (*) - Close to enemy going for it

                try:
                    closest_bonus = unit_closest_to(x, y)(world.bonuses)

                    if closest_bonus.type == BonusType.MEDIKIT:
                        bonus_profit = 250 + sqrt(1 - health_fraction) * 1250
                    elif closest_bonus.type == BonusType.REPAIR_KIT:
                        bonus_profit = 100 + sqrt(1 - hull_fraction) * 700
                    elif closest_bonus.type == BonusType.AMMO_CRATE:
                        bonus_profit = 500
                    else:
                        bonus_profit = 0

                    bonus_summand = max(0, bonus_profit)

                    if closest_bonus.get_distance_to(x, y) > 10:
                        bonus_summand = 0
                except:
                    #self.debug("!!! No bonuses on field")
                    bonus_summand = 0

                # How dangerous position is
                # + In centre of massacre
                # + Flying shells
                # + Turrets directed
                try:
                    positional_danger_penalty = - sum(map(lambda enemy: enemy.get_distance_to(x, y), enemies))/enemies_count * 1.8
                except:
                    self.debug("!!! All enemies were destroyed")
                    positional_danger_penalty = 0
                positional_danger_penalty += 1400

                if len(enemies) > 3 or health_fraction < 0.7 or hull_fraction < 0.6:
                    danger_penalty_factor = 1.4
                elif len(enemies) > 2 or health_fraction < 0.7 or hull_fraction < 0.6:
                    danger_penalty_factor = 1
                elif len(enemies) == 1 and health_fraction > 0.7 and hull_fraction > 0.5:
                    danger_penalty_factor = 0.2
                else:
                    danger_penalty_factor = 0.8
                positional_danger_penalty *= danger_penalty_factor

                turrets_danger_penalty = 0
                for enemy in enemies:
                    turrets_danger_penalty += attacked_area(x, y, enemy)
                turrets_danger_penalty *= 300

                # Flying shells
                flying_shell_penalty = 0
                for shell in world.shells:
                    if shell_will_hit_tank_going_to(shell, tank, x, y):
                        flying_shell_penalty = 1000

                stopping_penalty = 0
                if bonus_summand == 0:
                    stopping_penalty = (1 + max(0, 200 - tank.get_distance_to(x, y)))**1.2

                # If we're going somewhere, increase priority for this place
                if self.memory.last_target_position and distance(self.memory.last_target_position, (x, y)) < 30:
                    prev_target_bonus = 200
                else:
                    prev_target_bonus = 0

                # Don't stick to fucking edges
                edges_penalty = 2 * max(0, 150 - distance_to_edge(x, y, world))
                if x < 0 or y < 0 or x > world.width or y > world.height:
                    edges_penalty = 2000

                # Position priority:
                # + Bonus priority
                # - Dangerous position
                # - Close to screen edges
                # - Don't stay at the same place (*)
                est_time *= 2
                bonus_summand *= 1.5
                flying_shell_penalty *= 1
                stopping_penalty *= 1
                result = (2000 + bonus_summand + prev_target_bonus
                          - est_time - stopping_penalty - positional_danger_penalty - turrets_danger_penalty
                          - flying_shell_penalty - edges_penalty)
                if show_debug:
                    self.debug(('POS [%18s]: x=%8.2f, y=%8.2f, PT=%8.2f, bonus=%8.2f, est_time=%8.2f, ' +
                                'stoppingP=%8.2f, positional_P=%8.2f, TDP=%8.2f, FSP=%8.2f, edges=%8.2f, result=%8.2f') %
                                (name, x, y, prev_target_bonus, bonus_summand, est_time, stopping_penalty,
                                 positional_danger_penalty, turrets_danger_penalty, flying_shell_penalty, edges_penalty, result))
                return result

            pos_f = list(map(lambda pos: (pos[0], pos[1], pos[2], estimate_position_F(pos[0], pos[1])), positions))
            if DEBUG_MODE:
                estimate_position_F(tank.x, tank.y, show_debug=True)
                for pos in list(reversed(sorted(pos_f, key=operator.itemgetter(3))))[:6]:
                    estimate_position_F(pos[0], pos[1], name=pos[2], show_debug=True)
                for pos in pos_f:
                    if pos[2][:5] == "BONUS":
                        estimate_position_F(pos[0], pos[1], name=pos[2], show_debug=True)

            next_position = max(pos_f, key=operator.itemgetter(3))

            if self.memory.last_target_position:
                if distance((tank.x, tank.y), self.memory.last_target_position) < ANALYSIS_TARGET_SAVE_DISTANCE:
                    # We reached target
                    rtime = world.tick - self.memory.last_target_time
                    if rtime > 10:
                        self.analysis.store_target_reached(world, rtime)
                        self.debug("TARGET REACHED in %s" % rtime)
                    self.memory.last_target_time = world.tick

            if not self.memory.last_target_position or distance(self.memory.last_target_position, next_position) > DISTANCE_EPSILON:
                # We changed target
                self.memory.last_target_position = next_position[:2]
                self.memory.last_target_time = world.tick

                self.analysis.save_target_init_values(tank, next_position[0], next_position[1])

            self.debug("TGT (%8.2f, %8.2f) [%18s]; distance=%8.2f, ETA=%8.2f" %
                       (next_position[:3] + (tank.get_distance_to(*next_position[:2]), estimate_time_to_position(next_position[0], next_position[1], tank)) ))
            move_to_position(next_position[0], next_position[1], tank, move)

        def process_shooting():
            targets = filter(ALIVE_ENEMY_TANK, world.tanks)

            if not targets:
                return

            def get_target_priority(tank, target):
                health_fraction = tank.crew_health / tank.crew_max_health
                angle_penalty_factor = (1 + (1 - health_fraction) * 1.5 -
                                        (1 - max(0, 150 - tank.remaining_reloading_time)/150) * 1)

                angle_degrees = fabs(tank.get_turret_angle_to_unit(target)) / PI * 180
                result = - tank.get_distance_to_unit(target) / 10 - angle_penalty_factor * (angle_degrees**1.3)/2
                # Headshot ^_^
                if ((target.crew_health <= 20 or target.hull_durability <= 20) or
                    (tank.premium_shell_count > 0 and (target.crew_health < 35 or target.hull_durability <= 35))):
                    result += 25

                if attacked_area(tank.x, tank.y, target) > 0:
                    result += 15

                # Last target priority
                if self.memory.last_turret_target_id:
                    if self.memory.last_turret_target_id == target.id:
                        result += 5

                return result

            cur_target = max(targets, key=lambda t: get_target_priority(tank, t))
            self.memory.last_turret_target_id = cur_target.id

            est_pos = estimate_target_position(cur_target, tank)

            def bonus_attacked():
                for bonus in world.bonuses:
                    if (will_hit(tank, bonus, BONUS_FACTOR) and
                       tank.get_distance_to_unit(bonus) < tank.get_distance_to(*est_pos)):
                        return bonus
                return False

            def dead_tank_attacked():
                for obstacle in filter(DEAD_TANK, world.tanks):
                    next_position = estimate_target_position(obstacle, tank)
                    next_unit = fictive_unit(obstacle, next_position[0], next_position[1])
                    if (will_hit(tank, next_unit, DEAD_TANK_OBSTACLE_FACTOR) and
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

            if world.tick < 10:
                move.fire_type = FireType.NONE

            if fabs(cur_angle) > PI/180 * 0.5:
                move.turret_turn = sign(cur_angle)

        self.debug('========================= (Tick) #%s =====================' % world.tick)
        self.debug('Tank (x=%s, y=%s, health=%4s/%4s, super_shells=%2s)' %
                   (tank.x, tank.y, tank.crew_health, tank.crew_max_health, tank.premium_shell_count))

        process_moving()
        process_shooting()

        self.debug('Output: left: %5.2f, right: %5.2f' % (move.left_track_power, move.right_track_power))

        # processing velocity history
        #if world.tick % VELOCITY_ESTIMATION_PERIOD == 0:
        #    for object in world.tanks:
        #        slot = self.memory.velocity_history[object.id]
        #        slot.extend((object.speedX, object.speedY))
        #        if len(slot) > VELOCITY_ESTIMATION_COUNT:
        #            slot.popleft()


        #self.analysis.store_shell_velocity(world)

    def select_tank(self, tank_index, team_size):
        return TankType.MEDIUM