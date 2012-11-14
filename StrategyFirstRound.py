from StrategyScalarField import StrategyScalarField
from SimplePositionEstimators import *
from PostitionGetters import   TrivialPositionGetter, BasicPositionGetter, LightBasicPositionGetter, GridPositionGetter, BorderPositionGetter
from StrategicPositionEstimators import *

class StrategyOnePlayer5Enemies:

    def __init__(self, tank, world, memory, debug_on):
        self.strategy = StrategyScalarField(
            tank,
            world,
            [BasicPositionGetter(), BorderPositionGetter(7, 5, 80), GridPositionGetter(2, 2)],
            [
                BonusPositionEstimator(factor=1.2),
                LastTargetEstimator(150),
                TimeToPositionEstimator(4),
                PositionalPowerDangerEstimator(0.35, 9000),
                HideBehindEstimator(5000),
#                TurretsDangerEstimator(),
                FlyingShellEstimator(2000),
                EdgePenaltyEstimator(1000, 10),
            ],
            memory,
            debug_on
        )

    def change_state(self, *args, **kwargs):
        return self.strategy.change_state(*args, **kwargs)

    def make_turn(self, move):
        return self.strategy.make_turn(move)


class StrategyOnePlayer2Enemies:

    def __init__(self, tank, world, memory, debug_on):
        self.strategy = StrategyScalarField(
            tank,
            world,
            [BasicPositionGetter(), GridPositionGetter(7, 5)],
            [
                BonusPositionEstimator(factor=1.2),
                LastTargetEstimator(400),
                TimeToPositionEstimator(2),
                PositionalPowerDangerEstimator(0.35, 4000),
                TurretsDangerEstimator(),
                FlyingShellEstimator(2000),
                EdgePenaltyEstimator(1000, 60),
                AddConstantEstimator(3000)
            ],
            memory,
            debug_on
        )

    def change_state(self, *args, **kwargs):
        return self.strategy.change_state(*args, **kwargs)

    def make_turn(self, move):
        return self.strategy.make_turn(move)


class StrategyOnePlayerDuel:

    def __init__(self, tank, world, memory, debug_on):
        self.strategy = StrategyScalarField(
            tank,
            world,
            [BasicPositionGetter(), GridPositionGetter(7, 5)],
            [
                BonusPositionEstimator(factor=1.2),
                LastTargetEstimator(400),
                TimeToPositionEstimator(2),
                DuelPositionEstimator(1000),
                TurretsDangerEstimator(),
                FlyingShellEstimator(2000),
                EdgePenaltyEstimator(1000, 120),
                AddConstantEstimator(3000)
            ],
            memory,
            debug_on
        )

    def change_state(self, *args, **kwargs):
        return self.strategy.change_state(*args, **kwargs)

    def make_turn(self, move):
        return self.strategy.make_turn(move)