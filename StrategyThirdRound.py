from CompositeStrategy import make_composite_strategy
from StrategicPositionEstimators2P import Distance2PEstimator, FarDistancePenalty2P
from StrategicPositionEstimators3P import CloseDistancePenalty3P, BeAroundWeakestEnemy, HideBehindObstacle, BeAroundWeakestEnemyV2, AlliesDistance3P, CenterObstaclePenalty
from SimplePositionEstimators import *
from PostitionGetters import BasicPositionGetter, GridPositionGetter
from StrategicPositionEstimators import *
from StrategyScalarFieldMO import ScalarFieldMovingStrategy
from StrategyTargeting import EstimatorsTargetingStrategy
from TargetEstimators import DistancePenaltyTEstimator, FinishTEstimator, ResponseTEstimator, LastTargetTEstimator, AddConstantTEstimator, AnglePenaltyTEstimator, AttackWeakestTEstimator, BehindObstacleTEstimator, DebugSmartShootingTEstimator, DebugDangerousnessTEstimator, TargetConvenienceEstimator, AnglePenaltyTEstimatorV2
from TargetingClasses import OldShootDecisionMaker, ThirdRoundShootDecisionMaker

default_3R_position_getters = [BasicPositionGetter(35, 90), GridPositionGetter(7, 5, excluded=[(3, 3), (4, 3), (5, 3), (4, 4), (4, 2)])]

#old_targeting_strategy = EstimatorsTargetingStrategy(
#    [
#        AnglePenaltyTEstimator(),
#        DistancePenaltyTEstimator(),
#        FinishTEstimator(30),
#        ResponseTEstimator(),
#        LastTargetTEstimator(),
#        AddConstantTEstimator(180)
#    ],
#    OldShootDecisionMaker()
#)

third_round_targeting_strategy = EstimatorsTargetingStrategy(
    [
        AnglePenaltyTEstimatorV2(180),
        DistancePenaltyTEstimator(),
        BehindObstacleTEstimator(40),
        AttackWeakestTEstimator(40),
        DebugSmartShootingTEstimator(),
        DebugDangerousnessTEstimator(),
        #TargetConvenienceEstimator(30),
        AddConstantTEstimator(180)
    ],
    ThirdRoundShootDecisionMaker()
)

standard_position_estimators = [
    #HideBehindObstacle(250),
    EdgePenaltyEstimator(1000, 100),
    CenterObstaclePenalty(),
    FlyingShellEstimator(2000)
]

strategy_third_round = make_composite_strategy(
    ScalarFieldMovingStrategy(
        default_3R_position_getters,
        standard_position_estimators +
        [
            BonusPositionEstimator(factor=1.5, medikit_min=100, medikit_max=1500, repair_min=100, repair_max=900, ammo_crate=700),
            LastTargetEstimator(400),
            TimeToPositionEstimator(2),
            BeAroundWeakestEnemyV2(2000, 900, 600, 500),
            HideBehindObstacle(250),
            #SmartTurretsDangerEstimator(100, 400),
            SimpleTurretsDangerEstimator(400),
            AlliesDistance3P(250, 1100, 600, 1500)
        ]
    ),
    third_round_targeting_strategy,
    "Strategy R3"
)

strategy_third_round_prevail = make_composite_strategy(
    ScalarFieldMovingStrategy(
        default_3R_position_getters,
        standard_position_estimators +
        [
            BonusPositionEstimator(factor=1.4, medikit_min=100, medikit_max=1500, repair_min=100, repair_max=900, ammo_crate=700),
            LastTargetEstimator(400),
            TimeToPositionEstimator(2),
            BeAroundWeakestEnemyV2(2000, 800, 600, 500),
            #SmartTurretsDangerEstimator(100, 400),
            SimpleTurretsDangerEstimator(400),
            AlliesDistance3P(250, 1100, 600, 1500)
        ]
    ),
    third_round_targeting_strategy,
    "Strategy R3 Prevail"
)

strategy_third_round_total_prevail = make_composite_strategy(
    ScalarFieldMovingStrategy(
        default_3R_position_getters,
        standard_position_estimators +
        [
            BonusPositionEstimator(factor=1.3, medikit_min=100, medikit_max=1500, repair_min=100, repair_max=900, ammo_crate=700),
            LastTargetEstimator(400),
            TimeToPositionEstimator(2),
            BeAroundWeakestEnemyV2(2000, 300, 600, 500),
            #SmartTurretsDangerEstimator(100, 400),
            SimpleTurretsDangerEstimator(400),
            AlliesDistance3P(250, 1100, 600, 1500)
        ]
    ),
    third_round_targeting_strategy,
    "Strategy R3 Total Prevail"
)

strategy_third_round_two_left = make_composite_strategy(
    ScalarFieldMovingStrategy(
        default_3R_position_getters,
        standard_position_estimators +
        [
            BonusPositionEstimator(factor=1.5, medikit_min=100, medikit_max=1500, repair_min=100, repair_max=900, ammo_crate=700),
            LastTargetEstimator(400),
            TimeToPositionEstimator(2),
            BeAroundWeakestEnemyV2(2000, 900, 600, 500),
            #SmartTurretsDangerEstimator(100, 400),
            SimpleTurretsDangerEstimator(400),
            Distance2PEstimator(300, 120, 400, 200, 1000),
            FarDistancePenalty2P(600, 1000)
        ]
    ),
    third_round_targeting_strategy,
    "Strategy R3 2P"
)

strategy_third_round_two_left_prevail = make_composite_strategy(
    ScalarFieldMovingStrategy(
        default_3R_position_getters,
        standard_position_estimators +
        [
            BonusPositionEstimator(factor=1.2, medikit_min=100, medikit_max=1500, repair_min=100, repair_max=900, ammo_crate=700),
            LastTargetEstimator(400),
            TimeToPositionEstimator(2),
            BeAroundWeakestEnemyV2(2000, 700, 600, 500),
            #SmartTurretsDangerEstimator(100, 400),
            SimpleTurretsDangerEstimator(400),
            Distance2PEstimator(300, 120, 400, 200, 1000),
            FarDistancePenalty2P(600, 1000)
        ]
    ),
    third_round_targeting_strategy,
    "Strategy R3 2P Prevail"
)

strategy_third_round_last_man_standing = make_composite_strategy(
    ScalarFieldMovingStrategy(
        default_3R_position_getters,
        standard_position_estimators +
        [
            BonusPositionEstimator(factor=1.7, medikit_min=100, medikit_max=1500, repair_min=100, repair_max=900, ammo_crate=700),
            LastTargetEstimator(400),
            TimeToPositionEstimator(2),
            BeAroundWeakestEnemyV2(4000, 700, 600, 800),
            #SmartTurretsDangerEstimator(100, 400),
            SimpleTurretsDangerEstimator(400),
        ]
    ),
    third_round_targeting_strategy,
    "Strategy R3 2P Prevail"
)