from StrategyScalarField import StrategyScalarField
from SimplePositionEstimators import *
from PostitionGetters import TrivialPositionGetter, BasicPositionGetter, LightBasicPositionGetter
from StrategicPositionEstimators import *
from StrategicPositionEstimators2P import Distance2PEstimator

class StrategySecondRound:

    def __init__(self, tank, world, memory, debug_on):
        self.strategy = StrategyScalarField(
            tank,
            world,
            [BasicPositionGetter()],
            [
                BonusPosistionEstimator(1.2),
                LastTargetEstimator(400),
                TimeToPositionEstimator(2),
                PositionalDangerEstimator(),
                TurretsDangerEstimator(),
                FlyingShellEstimator(2000),
                EdgePenaltyEstimator(),
                Distance2PEstimator(500, 120, 300)
            ],
            memory,
            debug_on
        )

    def change_state(self, *args, **kwargs):
        return self.strategy.change_state(*args, **kwargs)

    def make_turn(self, move):
        return self.strategy.make_turn(move)