from math import hypot
from queue import PriorityQueue
import operator
from random import random
from GamePhysics import WorldPhysics, SHELL_ACCELERATION
from Geometry import Vector
from MyUtils import ALIVE_ENEMY_TANK, ALLY_TANK, solve_quadratic

# ================ CONSTANTS
# Moving
MAX_POSITION_ITERATIONS = 10

# Memorizing stuff
VELOCITY_ESTIMATION_PERIOD = 3
VELOCITY_ESTIMATION_COUNT = 10
class ScalarFieldMovingStrategy:
    def __init__(self, position_getters, position_estimators):
        self.position_getters = position_getters
        self.position_estimators = position_estimators

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
        self.est_time_cache = {}

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

        self.debug('=' * 16)
        if self.debug_mode:
            for shell in world.shells:
                v0 = hypot(shell.speedX, shell.speedY)
                a = SHELL_ACCELERATION
                d = tank.get_distance_to_unit(shell)
                tank_v = Vector(tank.x, tank.y)
                shell_v = Vector(shell.x, shell.y)
                shell_speed = Vector(shell.speedX, shell.speedY)
                #d = shell.get_distance_to(x, y)
                t = solve_quadratic(a/2, v0, -d)

                self.debug('SHELL [%12s] (%8.2f, %8.2f) v=%s, will hit=%s, hit time=%8.2f' %
                           (shell.player_name, shell.x, shell.y, shell_speed.length(), str(self.physics.shell_will_hit(shell, tank, factor=1.05)), t) )

            self.debug('=' * 16)