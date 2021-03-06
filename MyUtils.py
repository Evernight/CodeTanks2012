from math import hypot, sqrt
import operator
from json import dump, load, JSONEncoder
import os
from Geometry import numerically_zero
from model.Tank import Tank
from model.BonusType import BonusType
from model.TankType import TankType
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

def TANK(id):
    return lambda t: t.id == id

def filter_or(*filter_functions):
    return lambda t: any([f(t) for f in filter_functions])

def filter_and(*filter_functions):
    return lambda t: all([f(t) for f in filter_functions])

def fictive_unit(prototype, x, y, angle=None):
    if angle is None:
        angle = prototype.angle
    return Unit(0, prototype.width, prototype.height, x, y, 0, 0, angle, 0)

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

def inverse_dict(d, x):
    return list(map(operator.itemgetter(0), list(filter(lambda v: v[1] == x,  d.items()))))

def index_in_sorted(l, x):
    for item in enumerate(sorted(l)):
        if item[1] == x:
            return item[0]

def estimate_target_dangerousness(target):
    """
    target:
    0.4 : premium shells
    0.6 : health
    - low hull durability
    """
    target_danger = 0
    target_danger += 0.4 * min(1, target.premium_shell_count/3)
    target_danger += 0.6 * (target.crew_health/target.crew_max_health)**1.2
    if target.hull_durability > 60:
        hull_factor = 1
    elif target.hull_durability > 35:
        hull_factor = 0.7
    elif target.hull_durability > 20:
        hull_factor = 0.4
    else:
        hull_factor = 0.1
    target_danger *= hull_factor
    return target_danger

def target_dangerousness_for_tank(target, tank):
    return estimate_target_dangerousness(target) - estimate_target_dangerousness(tank)


def debug_dump(obj, fname):
    fullname= "../debug_dumps/"  + fname
    dir, file = os.path.split(fullname)

    try:
        os.makedirs(dir)
    except:
        pass
    with open(fullname, 'w') as f:
        class MyJSONEncoder(JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Tank):
                    return {
                        "__type__" : "Tank",
                        "x" : obj.x,
                        "y" : obj.y,
                        "angle" : obj.angle,
                        "turret_relative_angle" : obj.turret_relative_angle
                    }
                if isinstance(obj, Unit):
                    return {
                        "__type__" : "Unit",
                        "x" : obj.x,
                        "y" : obj.y,
                        "width" : obj.width,
                        "height" : obj.height,
                        "angle" : obj.angle
                    }
                return JSONEncoder.default(self, obj)
        dump(obj, f, cls=MyJSONEncoder)

def debug_dump_load(fname, relative=False):
    if relative:
        fullname = "../../debug_dumps/" + fname
    else:
        fullname = fname
    with open(fullname, 'r') as f:
        def decode_objects(d):
            if d.get("__type__") == "Tank":
                return Tank(0, "", 0, d["x"], d["y"], 0, 0, d["angle"], 0, d["turret_relative_angle"], 0, 0, 0, 0, 0, 0, TankType.MEDIUM)
            elif d.get("__type__") == "Unit":
                return Unit(0, d["width"], d["height"], d["x"], d["y"], 0, 0, d["angle"], 0)
            return d

        return load(f, object_hook=decode_objects)
