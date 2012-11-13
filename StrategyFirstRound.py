from StrategyScalarField import StrategyScalarField
from SimplePositionEstimators import *
from PostitionGetters import   TrivialPositionGetter, BasicPositionGetter, LightBasicPositionGetter
from StrategicPositionEstimators import *

class StrategyOnePlayer5Enemies:

    def __init__(self, tank, world, memory, debug_on):
        self.strategy = StrategyScalarField(
            tank,
            world,
            [BasicPositionGetter()],
            [
                BonusPositionEstimator(factor=1.2),
                LastTargetEstimator(400),
                TimeToPositionEstimator(2),
                PositionalPairDangerEstimator(2000),
                TurretsDangerEstimator(),
                FlyingShellEstimator(2000),
                EdgePenaltyEstimator(),
                AddConstantEstimator(3000)
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
            [BasicPositionGetter()],
            [
                BonusPositionEstimator(factor=1.2),
                LastTargetEstimator(400),
                TimeToPositionEstimator(2),
                PositionalDangerEstimator(),
                TurretsDangerEstimator(),
                FlyingShellEstimator(2000),
                EdgePenaltyEstimator(),
                AddConstantEstimator(3000)
            ],
            memory,
            debug_on
        )

    def change_state(self, *args, **kwargs):
        return self.strategy.change_state(*args, **kwargs)

    def make_turn(self, move):
        return self.strategy.make_turn(move)
