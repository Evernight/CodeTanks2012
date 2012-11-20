from math import hypot, sqrt
from Geometry import numerically_zero
from model import Tank
from model.BonusType import BonusType
from model.Unit import Unit

ALIVE_ENEMY_TANK = lambda t: not t.teammate and t.crew_health > 0 and t.hull_durability > 0
ALIVE_ALLY_TANK = lambda t: t.teammate and t.crew_health > 0 and t.hull_durability > 0
ENEMY_TANK = lambda t: not t.teammate
DEAD_TANK = lambda t: t.crew_health == 0 or t.hull_durability == 0
def ALLY_TANK(id):
    #TODO: make it work also for enemy tanks
    return lambda t: t.id != id and t.teammate

def NOT_TANK(id):
    return lambda t: t.id != id
UNIT_TO_POINT = lambda unit: (unit.x, unit.y)

def filter_or(*filter_functions):
    return lambda t: any([f(t) for f in filter_functions])

def filter_and(*filter_functions):
    return lambda t: all([f(t) for f in filter_functions])

def fictive_unit(prototype, x, y):
    return Unit(0, prototype.width, prototype.height, x, y, 0, 0, prototype.angle, 0)

def distance(c1, c2):
    return hypot(c1[0] - c2[0], c1[1] - c2[1])

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

def is_going_to_move(object):
    if type(object) == Tank:
        if object.crew_health > 0 and object.hull_durability > 0:
            return True
        else:
            return False
    return False

# ================================================================

def solve_quadratic(a, b, c):
    """
    Returns 0 if unsolvable or there are only negative roots
    """
    D = b*b - 4 * a * c
    if D < 0:
        return 0
    if numerically_zero(D):
        return -b/a
    r1, r2 = (-b + sqrt(D))/(2 * a), (-b - sqrt(D))/(2 * a)
    if r1 > 0:
        return r1
    else:
        if r2 > 0:
            return r2
        else:
            return 0

def lazy(func):
    @property
    def wrapper(self):
        attr_name = '__%s' % func.__name__
        try:
            value = getattr(self, attr_name)
        except AttributeError:
            value = func(self)
            setattr(self, attr_name, value)
        return value
    return wrapper