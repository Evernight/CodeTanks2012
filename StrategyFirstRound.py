from StrategyScalarField import StrategyScalarField
from field.SimplePositionEstimators import *
from field.PostitionGetters import BasicPositionGetter
from field.StrategicPositionEstimators import *

class StrategyFirstRound:

    def __init__(self, tank, world, memory, debug_on):
        self.strategy = StrategyScalarField(
            tank,
            world,
            BasicPositionGetter(),
            [
                BonusPosistionEstimator(1.2),
                LastTargetEstimator(),
                TimeToPositionEstimator(2),
                PositionalDangerEstimator(),
                TurretsDangerEstimator(),
                FlyingShellEstimator(),
                EdgePenaltyEstimator()
            ],
            memory,
            debug_on
        )

    def make_turn(self, move):
        return self.strategy.make_turn(move)