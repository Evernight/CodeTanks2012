from StrategyScalarField import StrategyScalarField
from SimplePositionEstimators import *
from PostitionGetters import TrivialPositionGetter, BasicPositionGetter, LightBasicPositionGetter
from StrategicPositionEstimators import *
from StrategicPositionEstimators2P import Distance2PEstimator, FarDistancePenalty2P

class StrategySecondRound4Enemies:

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
                Distance2PEstimator(300, 120, 300),
                FarDistancePenalty2P(600, 1000),
                AddConstantEstimator(3000),
            ],
            memory,
            debug_on
        )

    def change_state(self, *args, **kwargs):
        return self.strategy.change_state(*args, **kwargs)

    def make_turn(self, move):
        return self.strategy.make_turn(move)


class StrategySecondRound2Enemies:

    def __init__(self, tank, world, memory, debug_on):
        self.strategy = StrategyScalarField(
            tank,
            world,
            [BasicPositionGetter()],
            [
                BonusPositionEstimator(factor=1.4),
                LastTargetEstimator(400),
                TimeToPositionEstimator(2),
                PositionalDangerEstimator(),
                TurretsDangerEstimator(),
                FlyingShellEstimator(2000),
                EdgePenaltyEstimator(),
                Distance2PEstimator(300, 200, 600),
                AddConstantEstimator(3000),
                ],
            memory,
            debug_on
        )

    def change_state(self, *args, **kwargs):
        return self.strategy.change_state(*args, **kwargs)

    def make_turn(self, move):
        return self.strategy.make_turn(move)