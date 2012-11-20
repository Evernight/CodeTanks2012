from StrategicPositionEstimators2P import Distance2PEstimator
from StrategicPositionEstimators3P import CloseDistancePenalty3P, RunForEnemy, BeAroundWeakestEnemy, HideBehindObstacle
from StrategyScalarField import StrategyScalarField
from SimplePositionEstimators import *
from PostitionGetters import TrivialPositionGetter, BasicPositionGetter, LightBasicPositionGetter, GridPositionGetter
from StrategicPositionEstimators import *

class StrategyThirdRound:

    def __init__(self, tank, world, memory, debug_on):
        self.strategy = StrategyScalarField(
            tank,
            world,
            [BasicPositionGetter(30, 100), GridPositionGetter(7, 5)],
            [
                BonusPositionEstimator(factor=1.2, medikit_min=100, medikit_max=1500, repair_min=100, repair_max=900, ammo_crate=700),
                LastTargetEstimator(400),
                TimeToPositionEstimator(2),
                #PositionalPowerDangerEstimator(0.35, 5000),
                BeAroundWeakestEnemy(2000, 900, 300),
                HideBehindObstacle(250),
                SmartTurretsDangerEstimator(100, 400),
                FlyingShellEstimator(2000),
                EdgePenaltyEstimator(200, 300),
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


class StrategyThirdRoundTwoLeft:

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


class StrategyThirdWePrevail:

    def __init__(self, tank, world, memory, debug_on):
        self.strategy = StrategyScalarField(
            tank,
            world,
            [BasicPositionGetter(30, 100), GridPositionGetter(7, 5)],
            [
                BonusPositionEstimator(factor=1.2, medikit_min=100, medikit_max=1500, repair_min=100, repair_max=900, ammo_crate=700),
                LastTargetEstimator(300),
                TimeToPositionEstimator(2),
                RunForEnemy(1000),
                SmartTurretsDangerEstimator(100, 300),
                FlyingShellEstimator(2000),
                EdgePenaltyEstimator(200, 300),
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


class StrategyHeavy:

    def __init__(self, tank, world, memory, debug_on):
        self.strategy = StrategyScalarField(
            tank,
            world,
            [BasicPositionGetter(30, 70), GridPositionGetter(7, 5)],
            [
                BonusPositionEstimator(factor=0.6, medikit_min=100, medikit_max=1500, repair_min=100, repair_max=900, ammo_crate=700),
                LastTargetEstimator(200),
                TimeToPositionEstimator(2),
                #SmartTurretsDangerEstimator(100, 300),
                #FlyingShellEstimator(2000),
                #EdgePenaltyEstimator(1000, 60),
                CloseDistancePenalty3P(200, 1000),
                RunForEnemy(1500),
                AddConstantEstimator(3000),
                ],
            memory,
            debug_on
        )

    def change_state(self, *args, **kwargs):
        return self.strategy.change_state(*args, **kwargs)

    def make_turn(self, move):
        return self.strategy.make_turn(move)
