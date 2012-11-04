from model.BonusType import BonusType
from model.Unit import Unit
from GamePhysics import *

ALIVE_ENEMY_TANK = lambda t: not t.teammate and t.crew_health > 0 and t.hull_durability > 0
ENEMY_TANK = lambda t: not t.teammate
DEAD_TANK = lambda t: t.crew_health == 0 or t.hull_durability == 0
UNIT_TO_POINT = lambda unit: (unit.x, unit.y)

def fictive_unit(prototype, x, y):
    return Unit(0, prototype.width, prototype.height, x, y, 0, 0, prototype.angle, 0)

def closest_to(coord):
    return lambda arg: min(arg, key=lambda item: distance(item, coord))

def unit_closest_to(x, y):
    return lambda arg: min(arg, key=lambda item: item.get_distance_to(x, y))

def bonus_name_by_type(type):
    return {
        BonusType.MEDIKIT    : "MEDIKIT",
        BonusType.REPAIR_KIT : "REPAIR_KIT",
        BonusType.AMMO_CRATE : "AMMO_CRATE"
    }[type]