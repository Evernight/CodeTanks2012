from StrategyScalarField import StrategyScalarField
from SimplePositionEstimators import *
from PostitionGetters import *
from StrategicPositionEstimators import *
from StrategicPositionEstimators2P import Distance2PEstimator, FarDistancePenalty2P
from StrategyTargeting import EstimatorsTargetingStrategy
from TargetEstimators import *
from TargetingClasses import OldShootDecisionMaker

old_targeting_strategy = EstimatorsTargetingStrategy(
    [
        AnglePenaltyTEstimator(),
        DistancePenaltyTEstimator(),
        FinishTEstimator(30),
        ResponseTEstimator(),
        LastTargetTEstimator(),
        AddConstantTEstimator(180)
    ],
    OldShootDecisionMaker()
)

class StrategySecondRound4Enemies:

    def __init__(self, tank, world, memory, debug_on):
        self.strategy = StrategyScalarField(
            tank,
            world,
            [BasicPositionGetter(), GridPositionGetter(7, 5)],
            [
                BonusPositionEstimator(factor=1.2, ammo_crate=700, repair_max=900),
                LastTargetEstimator(400),
                TimeToPositionEstimator(2),
                PositionalPowerDangerEstimator(0.35, 6000),
                TurretsDangerEstimator(),
                FlyingShellEstimator(2000),
                EdgePenaltyEstimator(1000, 60),
                Distance2PEstimator(300, 120, 400, 200, 1000),
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
            [BasicPositionGetter(), GridPositionGetter(7, 5)],
            [
                BonusPositionEstimator(factor=1.4, ammo_crate=800, repair_max=1100),
                LastTargetEstimator(400),
                TimeToPositionEstimator(2),
                PositionalPowerDangerEstimator(0.35, 4000),
                TurretsDangerEstimator(),
                FlyingShellEstimator(2000),
                EdgePenaltyEstimator(1000, 100),
                Distance2PEstimator(400, 200, 700, 200, 1000),
                AddConstantEstimator(3000),
                ],
            memory,
            debug_on
        )

    def change_state(self, *args, **kwargs):
        return self.strategy.change_state(*args, **kwargs)

    def make_turn(self, move):
        return self.strategy.make_turn(move)