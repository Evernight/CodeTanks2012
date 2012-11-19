from StrategicPositionEstimators3P import CloseDistancePenalty3P
from StrategyScalarField import StrategyScalarField
from SimplePositionEstimators import *
from PostitionGetters import TrivialPositionGetter, BasicPositionGetter, LightBasicPositionGetter, GridPositionGetter
from StrategicPositionEstimators import *

class StrategyThirdRound:

    def __init__(self, tank, world, memory, debug_on):
        self.strategy = StrategyScalarField(
            tank,
            world,
            [BasicPositionGetter(30, 70), GridPositionGetter(7, 5)],
            [
                BonusPositionEstimator(factor=1.2, medikit_min=100, medikit_max=1500, repair_min=100, repair_max=900, ammo_crate=700),
                LastTargetEstimator(300),
                TimeToPositionEstimator(2),
                PositionalPowerDangerEstimator(0.35, 5000),
                SmartTurretsDangerEstimator(100, 300),
                FlyingShellEstimator(2000),
                EdgePenaltyEstimator(1000, 60),
                CloseDistancePenalty3P(200, 1000),
                AddConstantEstimator(3000),
            ],
            memory,
            debug_on
        )

    def change_state(self, *args, **kwargs):
        return self.strategy.change_state(*args, **kwargs)

    def make_turn(self, move):
        return self.strategy.make_turn(move)
