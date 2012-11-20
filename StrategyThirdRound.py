from StrategicPositionEstimators2P import Distance2PEstimator, FarDistancePenalty2P
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
            [BasicPositionGetter(35, 90), GridPositionGetter(7, 5)],
            [
                BonusPositionEstimator(factor=1.5, medikit_min=100, medikit_max=1500, repair_min=100, repair_max=900, ammo_crate=700),
                LastTargetEstimator(400),
                TimeToPositionEstimator(2),
                BeAroundWeakestEnemy(4000, 900, 600),
                HideBehindObstacle(250),
                SmartTurretsDangerEstimator(50, 200),
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


class StrategyThirdRoundPrevail:

    def __init__(self, tank, world, memory, debug_on):
        self.strategy = StrategyScalarField(
            tank,
            world,
            [BasicPositionGetter(35, 90), GridPositionGetter(7, 5)],
            [
                BonusPositionEstimator(factor=1.4, medikit_min=100, medikit_max=1500, repair_min=100, repair_max=900, ammo_crate=700),
                LastTargetEstimator(400),
                TimeToPositionEstimator(2),
                BeAroundWeakestEnemy(4000, 600, 600),
                HideBehindObstacle(250),
                SmartTurretsDangerEstimator(100, 400),
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

class StrategyThirdRoundTotalPrevail:

    def __init__(self, tank, world, memory, debug_on):
        self.strategy = StrategyScalarField(
            tank,
            world,
            [BasicPositionGetter(35, 90), GridPositionGetter(7, 5)],
            [
                BonusPositionEstimator(factor=1.3, medikit_min=100, medikit_max=1500, repair_min=100, repair_max=900, ammo_crate=700),
                LastTargetEstimator(400),
                TimeToPositionEstimator(2),
                BeAroundWeakestEnemy(4000, 200, 600),
                HideBehindObstacle(250),
                SmartTurretsDangerEstimator(100, 400),
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


class StrategyThirdRoundTwoLeft:

    def __init__(self, tank, world, memory, debug_on):
        self.strategy = StrategyScalarField(
            tank,
            world,
            [BasicPositionGetter(35, 90), GridPositionGetter(7, 5)],
            [
                BonusPositionEstimator(factor=1.5, medikit_min=100, medikit_max=1500, repair_min=100, repair_max=900, ammo_crate=700),
                LastTargetEstimator(400),
                TimeToPositionEstimator(2),
                BeAroundWeakestEnemy(4000, 1000, 600),
                HideBehindObstacle(250),
                SmartTurretsDangerEstimator(100, 400),
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

class StrategyThirdRoundTwoLeftPrevail:

    def __init__(self, tank, world, memory, debug_on):
        self.strategy = StrategyScalarField(
            tank,
            world,
            [BasicPositionGetter(35, 90), GridPositionGetter(7, 5)],
            [
                BonusPositionEstimator(factor=1.2, medikit_min=100, medikit_max=1500, repair_min=100, repair_max=900, ammo_crate=700),
                LastTargetEstimator(400),
                TimeToPositionEstimator(2),
                BeAroundWeakestEnemy(4000, 300, 300),
                HideBehindObstacle(250),
                SmartTurretsDangerEstimator(100, 400),
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