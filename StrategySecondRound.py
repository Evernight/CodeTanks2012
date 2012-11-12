from StrategyScalarField import StrategyScalarField
from field.SimplePositionEstimators import *
from field.PostitionGetters import BasicPositionGetter
from field.StrategicPositionEstimators import *
from field.StrategicPositionEstimators2P import Distance2PEstimator

class StrategySecondRound:

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
                EdgePenaltyEstimator(),
                Distance2PEstimator(500, 120, 300)
            ],
            memory,
            debug_on
        )

    def make_turn(self, move):
        return self.strategy.make_turn(move)