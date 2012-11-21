from CompositeStrategy import make_composite_strategy
from StrategicPositionEstimators2P import Distance2PEstimator, FarDistancePenalty2P
from StrategicPositionEstimators3P import CloseDistancePenalty3P, BeAroundWeakestEnemy, HideBehindObstacle
from SimplePositionEstimators import *
from PostitionGetters import BasicPositionGetter, GridPositionGetter
from StrategicPositionEstimators import *
from StrategyScalarFieldMO import ScalarFieldMovingStrategy
from StrategyTargeting import EstimatorsTargetingStrategy
from TargetEstimators import DistancePenaltyTEstimator, FinishTEstimator, ResponseTEstimator, LastTargetTEstimator, AddConstantTEstimator, AnglePenaltyTEstimator, AttackWeakestTEstimator, BehindObstacleTEstimator, DebugVarianceTEstimator, DebugTargetSpeedTEstimator
from TargetingClasses import OldShootDecisionMaker, ThirdRoundShootDecisionMaker

default_3R_position_getters = [BasicPositionGetter(35, 90), GridPositionGetter(7, 5, excluded=[(4, 3)])]

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

third_round_targeting_strategy = EstimatorsTargetingStrategy(
    [
        AnglePenaltyTEstimator(),
        DistancePenaltyTEstimator(),
        BehindObstacleTEstimator(20),
        AttackWeakestTEstimator(50),
        DebugVarianceTEstimator(),
        DebugTargetSpeedTEstimator(),
        AddConstantTEstimator(180)
    ],
    ThirdRoundShootDecisionMaker()
)

strategy_third_round = make_composite_strategy(
    ScalarFieldMovingStrategy(
        default_3R_position_getters,
        [
            BonusPositionEstimator(factor=1.5, medikit_min=100, medikit_max=1500, repair_min=100, repair_max=900, ammo_crate=700),
            LastTargetEstimator(400),
            TimeToPositionEstimator(2),
            BeAroundWeakestEnemy(4000, 900, 600),
            HideBehindObstacle(250),
            SmartTurretsDangerEstimator(100, 400),
            FlyingShellEstimator(2000),
            EdgePenaltyEstimator(1000, 60),
            CloseDistancePenalty3P(200, 1000),
        ]
    ),
    third_round_targeting_strategy,
    "Strategy R3"
)

strategy_third_round_prevail = make_composite_strategy(
    ScalarFieldMovingStrategy(
        default_3R_position_getters,
        [
            BonusPositionEstimator(factor=1.4, medikit_min=100, medikit_max=1500, repair_min=100, repair_max=900, ammo_crate=700),
            LastTargetEstimator(400),
            TimeToPositionEstimator(2),
            BeAroundWeakestEnemy(4000, 800, 600),
            HideBehindObstacle(250),
            SmartTurretsDangerEstimator(100, 400),
            FlyingShellEstimator(2000),
            EdgePenaltyEstimator(1000, 60),
            CloseDistancePenalty3P(200, 1000),
            AddConstantEstimator(3000)
        ]
    ),
    third_round_targeting_strategy,
    "Strategy R3 Prevail"
)

strategy_third_round_total_prevail = make_composite_strategy(
    ScalarFieldMovingStrategy(
        default_3R_position_getters,
        [
            BonusPositionEstimator(factor=1.3, medikit_min=100, medikit_max=1500, repair_min=100, repair_max=900, ammo_crate=700),
            LastTargetEstimator(400),
            TimeToPositionEstimator(2),
            BeAroundWeakestEnemy(4000, 300, 600),
            HideBehindObstacle(250),
            SmartTurretsDangerEstimator(100, 400),
            FlyingShellEstimator(2000),
            EdgePenaltyEstimator(1000, 60),
            CloseDistancePenalty3P(200, 1000),
        ]
    ),
    third_round_targeting_strategy,
    "Strategy R3 Total Prevail"
)

strategy_third_round_two_left = make_composite_strategy(
    ScalarFieldMovingStrategy(
        default_3R_position_getters,
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
        ]
    ),
    third_round_targeting_strategy,
    "Strategy R3 2P"
)

strategy_third_round_two_left_prevail = make_composite_strategy(
    ScalarFieldMovingStrategy(
        default_3R_position_getters,
        [
            BonusPositionEstimator(factor=1.2, medikit_min=100, medikit_max=1500, repair_min=100, repair_max=900, ammo_crate=700),
            LastTargetEstimator(400),
            TimeToPositionEstimator(2),
            BeAroundWeakestEnemy(4000, 700, 300),
            HideBehindObstacle(250),
            SmartTurretsDangerEstimator(100, 400),
            FlyingShellEstimator(2000),
            EdgePenaltyEstimator(1000, 60),
            Distance2PEstimator(300, 120, 400, 200, 1000),
            FarDistancePenalty2P(600, 1000),
        ]
    ),
    third_round_targeting_strategy,
    "Strategy R3 2P Prevail"
)
