from MyUtils import ALLY_TANK, DEAD_TANK, ALIVE_ENEMY_TANK
from StrategyFirstRound import StrategyOnePlayer5Enemies, StrategyOnePlayer2Enemies, StrategyOnePlayerDuel
from StrategySecondRound import StrategySecondRound
from WorldAnalysis import PhysicsAnalyser
from model.TankType import TankType
from collections import deque, defaultdict

# TODO:
# * shell will hit fix
# * aggression bonus
# * new safety function in 2p game
# * 2p targets smart choice
#  * velocity extrapolating + estimate ability to predict target position

#  * alternate unreachable targets

#  * realistic moving and time estimation (mechanics)
#  * take target orientation into account when shooting / orientation of the tank
#  * when targeting take current moving destination into account (or the opposite)
#  * different modes of behaviour
#  * remove bonuses I'll fail to get because of exist time from targets
#  * even more precise short distance estimation?
#  * profiling again?
#  * fix "stucked" position
#  * defensive mode?

if __debug__:
    DEBUG_MODE = True
else:
    DEBUG_MODE = False
PHYSICS_RESEARCH_MODE = False

# ================ CONSTANTS
# Phys analysis
ANALYSIS_TARGET_SAVE_DISTANCE = 80

# Utils
class MyStrategy:

    class Memory:
        def __init__(self):
            self.velocity_history = defaultdict(deque)
            self.last_target_position = None
            self.last_turret_target_id = None

    def __init__(self):
        self.memory = MyStrategy.Memory()
        self.analysis = PhysicsAnalyser(PHYSICS_RESEARCH_MODE)

        self.str1 = None
        self.str2 = None

    def debug(self, message, ticks_period=5):
        if self.world.tick % ticks_period == 0:
            if DEBUG_MODE:
                print(message)

    def move(self, tank, world, move):
        self.world = world

        self.debug('')
        self.debug('#' * 64)
        self.debug('========================= (Tick) #%-4s =========================' % world.tick)
        self.debug('Tank %s (x=%s, y=%s, health=%4s/%4s, hull=%4s/%4s, super_shells=%2s, reload=%3s/%3s)' %
                   (tank.teammate_index, tank.x, tank.y, tank.crew_health, tank.crew_max_health,
                    tank.hull_durability, tank.hull_max_durability, tank.premium_shell_count,
                    tank.remaining_reloading_time, tank.reloading_time))
        self.debug('#' * 64)

        if DEAD_TANK(tank):
            self.debug('DEAD x_x')
            return

        tanks = world.tanks

        allies = list(filter(ALLY_TANK(tank.id), tanks))
        enemies = list(filter(ALIVE_ENEMY_TANK, tanks))
        if len(allies) == 1 and not DEAD_TANK(allies[0]):
            StrategySecondRound(tank, world, self.memory, DEBUG_MODE).make_turn(move)
        else:
            if len(enemies) > 3:
                StrategyOnePlayer5Enemies(tank, world, self.memory, DEBUG_MODE).make_turn(move)
            elif len(enemies) > 1:
                StrategyOnePlayer2Enemies(tank, world, self.memory, DEBUG_MODE).make_turn(move)
            else:
                StrategyOnePlayerDuel(tank, world, self.memory, DEBUG_MODE).make_turn(move)

        self.debug('_' * 64)
        self.debug('Output: left: %5.2f, right: %5.2f' % (move.left_track_power, move.right_track_power))

    def select_tank(self, tank_index, team_size):
        return TankType.MEDIUM