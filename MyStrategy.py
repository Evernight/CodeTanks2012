from MyUtils import ALLY_TANK, DEAD_TANK, ALIVE_ENEMY_TANK
from StrategyFirstRound import StrategyOnePlayer5Enemies, StrategyOnePlayer2Enemies, StrategyOnePlayerDuel
from StrategySecondRound import StrategySecondRound4Enemies, StrategySecondRound2Enemies
from StrategyThirdRound import StrategyThirdRound, StrategyHeavy, StrategyThirdRoundTwoLeft
from WorldAnalysis import PhysicsAnalyser
from model.TankType import TankType
from collections import deque, defaultdict

# TODO:
# * new safety function in 2p game

# * hide behind tanks

# * velocity extrapolating + estimate ability to predict target position
# * synchronize moving and shooting

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

HEAVY_TANK_TEST = 1
TEST_STRATEGY = 0

# ================ CONSTANTS
# Phys analysis
ANALYSIS_TARGET_SAVE_DISTANCE = 80

# Utils
class MyStrategy:

    class Memory:
        def __init__(self):
            self.velocity_history = defaultdict(deque)
            self.last_target_position = {}
            self.last_turret_target_id = None

    def __init__(self):
        self.memory = MyStrategy.Memory()
        self.analysis = PhysicsAnalyser(PHYSICS_RESEARCH_MODE)

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

        if len(world.players) == 2:
            # MAIN
            if len(allies) == 2:
                strategy = StrategyThirdRound(tank, world, self.memory, DEBUG_MODE)
            elif len(allies) == 1:
                strategy = StrategyThirdRoundTwoLeft(tank, world, self.memory, DEBUG_MODE)
            else:
                if len(enemies) > 1:
                    strategy = StrategyOnePlayer2Enemies(tank, world, self.memory, DEBUG_MODE)
                else:
                    strategy = StrategyOnePlayerDuel(tank, world, self.memory, DEBUG_MODE)

        elif len(allies) == 1 and not DEAD_TANK(allies[0]):
            if len(enemies) > 2:
                strategy = StrategySecondRound4Enemies(tank, world, self.memory, DEBUG_MODE)
            elif len(enemies) > 1:
                strategy = StrategySecondRound2Enemies(tank, world, self.memory, DEBUG_MODE)
            else:
                strategy = StrategyOnePlayerDuel(tank, world, self.memory, DEBUG_MODE)
        else:
            if len(enemies) > 3:
                strategy = StrategyOnePlayer5Enemies(tank, world, self.memory, DEBUG_MODE)
            elif len(enemies) > 1:
                strategy = StrategyOnePlayer2Enemies(tank, world, self.memory, DEBUG_MODE)
            else:
                strategy = StrategyOnePlayerDuel(tank, world, self.memory, DEBUG_MODE)
        strategy.make_turn(move)

        self.debug('_' * 64)
        self.debug('Output: left: %5.2f, right: %5.2f' % (move.left_track_power, move.right_track_power))

        #self.analysis.store_shell_velocity(world)

    def select_tank(self, tank_index, team_size):
        if team_size == 3:
            if TEST_STRATEGY == HEAVY_TANK_TEST:
                return TankType.HEAVY

        return TankType.HEAVY