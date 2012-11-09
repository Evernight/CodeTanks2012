from math import pi as PI, fabs, degrees, sqrt, hypot
from Geometry import Vector, sign, numerically_zero
from MyUtils import fictive_unit, is_going_to_move, NOT_TANK

SHELL_VELOCITY = 14
SHELL_ACCELERATION = -0.08
INITIAL_SHELL_VELOCITY = 16.58333316713906

BACKWARDS_THRESHOLD = 3 * PI / 5
TARGET_REACHED_DISTANCE = 20
DISTANCE_EPSILON = 1

TIME_ESTIMATION_COEF = (93.118, 0.441, 11.347, -4.311, -45.925, -93.353, -22.895, 22.271 + 20)

def distance(c1, c2):
    return hypot(c1[0] - c2[0], c1[1] - c2[1])

def distance_to_edge(x, y, world):
    return min(x, world.width - x, y, world.height - y)

TIME_ESTIMATION_ANGLE_PENALTY = 30
TIME_ESTIMATION_VELOCITY_FACTOR = 20

LOW_ANGLE = PI/16
FICTIVE_ACCELERATION = 0.7
def estimate_time_to_position(x, y, tank):
    dist = tank.get_distance_to(x, y)
    vt = Vector(tank.speedX, tank.speedY)

    tank_v = Vector(tank.x, tank.y)
    pt_v = Vector(x, y)
    d = pt_v - tank_v

    if d.is_zero():
        return 0

    tank_d_v = Vector(1, 0).rotate(tank.angle)

    if vt.is_zero() or d.is_zero():
        vd_angle = 0
    else:
        vd_angle = vt.angle(d)

    if tank_d_v.is_zero() or d.is_zero():
        d_angle = 0
    else:
        d_angle = tank_d_v.angle(d)

    # Short distances fix
    if dist < 100:
        if fabs(d_angle) < LOW_ANGLE:
            v0 = vt.projection(d)
            return solve_quadratic(FICTIVE_ACCELERATION/2, v0, -dist)
            #return dist/6
        elif PI - fabs(d_angle) < LOW_ANGLE:
            v0 = vt.projection(d)
            return solve_quadratic(FICTIVE_ACCELERATION/2 * 0.75, v0, -dist)
            #return dist/6 /0.75


    if d.is_zero():
        values = (0, 0, 0, 0, 0, 0, 0, 1)
    else:

        values = (
            d_angle,
            dist,
            vd_angle,
            vt.length(),
            tank.angular_speed,
            tank.crew_health/tank.crew_max_health,
            d_angle ** 2,
            1
        )

    return sum([x * y for (x, y) in zip(values, TIME_ESTIMATION_COEF)])

def estimate_target_position(target, tank):
    """
    For shooting
    """
    v0 = INITIAL_SHELL_VELOCITY
    a = SHELL_ACCELERATION
    coord = (target.x, target.y)
    for i in range(4):
        d = tank.get_distance_to(coord[0], coord[1])
        try:
            t = (sqrt(v0**2 + 2*a*d) - v0)/a
        except:
            t = -v0/a
        coord = (target.x + target.speedX * t, target.y + target.speedY * t)
    return coord

def move_to_position(x, y, tank, move):
    if tank.get_distance_to(x, y) < TARGET_REACHED_DISTANCE:
        return 0, 0

    angle = tank.get_angle_to(x, y)
    dist = tank.get_distance_to(x, y)

    def get_values(angle, multiplier=1):
        #if fabs(angle) < PI/6 and fabs(tank.angular_speed) < 0.02:
        #    left, right = 1, 1
        #else:
        #    left, right = 1, -1
        if dist < 300:
            left, right = 1, 1 - 6 * angle / PI
        elif dist < 700:
            # Dirty fix for now (long distance)
            left, right = 1, 1 - 4.5 * angle / PI
            if fabs(tank.angular_speed) > 0.025:
                left, right = 1, 1 - 2 * angle / PI
        else:
            # Dirty fix for now (long distance)
            left, right = 1, 1 - 3 * angle / PI
            if fabs(tank.angular_speed) > 0.02:
                left, right = 1, 1 - 2 * angle / PI

        return left * multiplier, right * multiplier

    #print('angle=%s, dist=%s' % (angle, dist))
    if (fabs(angle) > 5*PI/6 and dist < 800) or (fabs(angle) > BACKWARDS_THRESHOLD and dist < 500) or (fabs(angle) > PI/2 and dist < 200):
        if angle > 0:
            move.left_track_power, move.right_track_power = get_values(PI - fabs(angle), -1)
        else:
            move.right_track_power, move.left_track_power = get_values(PI - fabs(angle), -1)
    else:
        if angle > 0:
            move.left_track_power, move.right_track_power = get_values(fabs(angle))
        else:
            move.right_track_power, move.left_track_power = get_values(fabs(angle))

def will_hit(tank, target, factor=1):
    """
    Returns True if tank will hit rectangular object
    """
    b = tank.angle + tank.turret_relative_angle
    e = Vector(1, 0)
    q = e.rotate(b)

    center = Vector(target.x - tank.x, target.y - tank.y)
    if center.scalar_product(q) < 0:
        return False

    a = target.angle

    c1 = center + Vector(target.width/2 * factor, target.height/2 * factor).rotate(a)
    c2 = center + Vector(- target.width/2 * factor, target.height/2 * factor).rotate(a)
    c3 = center + Vector(- target.width/2 * factor, - target.height/2 * factor).rotate(a)
    c4 = center + Vector(target.width/2 * factor, - target.height/2 * factor).rotate(a)
    if sign(c1.cross_product(q)) == sign(q.cross_product(c3)):
        #print("TEST", c1, c2, c3, c4, q)
        return True
    if sign(c2.cross_product(q)) == sign(q.cross_product(c4)):
        #print("TEST", c1, c2, c3, c4, q)
        return True
    return False

def vector_is_intersecting_object(p, d, target, factor=1):
    center = Vector(target.x - p.x, target.y - p.y)
    if center.scalar_product(d) < 0:
        return False

    a = target.angle

    c1 = center + Vector(target.width/2 * factor, target.height/2 * factor).rotate(a)
    c2 = center + Vector(- target.width/2 * factor, target.height/2 * factor).rotate(a)
    c3 = center + Vector(- target.width/2 * factor, - target.height/2 * factor).rotate(a)
    c4 = center + Vector(target.width/2 * factor, - target.height/2 * factor).rotate(a)
    if sign(c1.cross_product(d)) == sign(d.cross_product(c3)):
        return True
    if sign(c2.cross_product(d)) == sign(d.cross_product(c4)):
        return True
    return False


def shell_will_hit(shell, target, factor=1):
    """
    Returns True if shell will hit rectangular object
    """
    b = shell.angle
    e = Vector(1, 0)
    q = e.rotate(b)

    center = Vector(target.x - shell.x, target.y - shell.y)
    if center.scalar_product(q) < 0:
        return False

    a = target.angle

    c1 = center + Vector(target.width/2 * factor, target.height/2 * factor).rotate(a)
    c2 = center + Vector(- target.width/2 * factor, target.height/2 * factor).rotate(a)
    c3 = center + Vector(- target.width/2 * factor, - target.height/2 * factor).rotate(a)
    c4 = center + Vector(target.width/2 * factor, - target.height/2 * factor).rotate(a)
    if sign(c1.cross_product(q)) == sign(q.cross_product(c3)):
        #print("TEST", c1, c2, c3, c4, q)
        return True
    if sign(c2.cross_product(q)) == sign(q.cross_product(c4)):
        #print("TEST", c1, c2, c3, c4, q)
        return True
    return False


# Check if area is attacked by some motherfucker
DANGEROUS_WIDTH = 110
class EnemyAttackedChecker:
    def __init__(self, enemy):
        self.enemy_v = Vector(enemy.x, enemy.y)
        self.turret_v = Vector(1, 0).rotate(enemy.angle + enemy.turret_relative_angle)
        td = self.turret_v.rotate(PI/2) * DANGEROUS_WIDTH / 2
        self.p1 = self.enemy_v + td
        self.p2 = self.enemy_v - td

    def attacked_area(self, x, y):
        pt_v = Vector(x, y)
        if (pt_v - self.enemy_v).scalar_product(self.turret_v) <= 0:
            return 0
        if sign(self.turret_v.cross_product(pt_v - self.p1)) == sign(self.turret_v.cross_product(pt_v - self.p2)):
            return 0
        else:
            return 1

class ContinuousEnemyAttackedChecker:
    def __init__(self, enemy):
        self.enemy_v = Vector(enemy.x, enemy.y)
        self.turret_v = Vector(1, 0).rotate(enemy.angle + enemy.turret_relative_angle)

    def attacked_area(self, x, y):
        pt_v = Vector(x, y)
        if (pt_v - self.enemy_v).scalar_product(self.turret_v) <= 0:
            return 0
        dist = pt_v.distance(self.enemy_v, self.turret_v)
        return max(0, (DANGEROUS_WIDTH - dist)/DANGEROUS_WIDTH)

def attacked_area(x, y, enemy, cache=None):
    """
    Rectangle shape
    """
    if cache is None or not enemy.id in cache:
        cache[enemy.id] = ContinuousEnemyAttackedChecker(enemy)
    return cache[enemy.id].attacked_area(x, y)

def shell_will_hit_tank_going_to(shell, tank, x, y, et=None, name='?'):
    """
    WTF is written here???
    """
    if et is None:
        et = estimate_time_to_position(x, y, tank)

    dist = tank.get_distance_to(x, y)

    v0 = hypot(shell.speedX, shell.speedY)
    a = SHELL_ACCELERATION
    d = tank.get_distance_to_unit(shell)
    #d = shell.get_distance_to(x, y)
    t = solve_quadratic(a/2, v0, -d)


    if shell_will_hit(shell, tank) and et > t:
        #if tank.get_distance_to(x, y) < 81:
        #    print('HIT [%s] x=%s, y=%s, et=%s, t=%s, d_shell=%s, v0=%s, d_pos=%s' % (name, x, y, et, t, d, v0, tank.get_distance_to(x, y)))
        return True
    #if shell_will_hit(shell, fictive_unit(tank, next_pos.x, next_pos.y)):
    #    if tank.get_distance_to(x, y) < 81:
    #        print('HIT [%s] x=%s, y=%s, et=%s, t=%s, d_shell=%s, v0=%s, d_pos=%s' % (name, x, y, et, t, d, v0, tank.get_distance_to(x, y)))
    #    return True
    if dist < 150:
        # short distance
        return shell_will_hit(shell, fictive_unit(tank, x, y))
    else:
        # long distance, check if our direction is intersecting segment
        pt_v = Vector(x, y)
        tank_v = Vector(tank.x, tank.y)
        dir = tank_v - pt_v
        shell_v = Vector(shell.x, shell.y)
        shell_speed = Vector(shell.speedX, shell.speedY)
        next_shell = shell_v + shell_speed * t
        if sign((shell_v - tank_v).cross_product(dir)) == sign(dir.cross_product(next_shell - tank_v)):
            return True
        else:
            return False

def position_is_blocked(x, y, tank, world):
    #if tank.get_distance_to(x, y) > 400:
    #    return False
    tank_v = Vector(tank.x, tank.y)
    p = Vector(x, y)
    dist = tank.get_distance_to(x, y)
    if (p - tank_v).is_zero():
        return False
    for obj in filter(NOT_TANK(tank.id), world.tanks):
        obj_dist = tank.get_distance_to_unit(obj)
        if vector_is_intersecting_object(tank_v, p - tank_v, obj, factor=1.2) and obj_dist < dist:
            if not is_going_to_move(obj):
                return True
            if obj_dist < 100:
                return True
    return False

SHIFT_DISTANCE = 100
def get_new_positions(pos, tank):
    x, y = pos[:2]
    tank_v = Vector(tank.x, tank.y)
    p = Vector(x, y)
    d = p - tank_v

    p1 = tank_v + d/2 + d.normalize().rotate(PI/2) * SHIFT_DISTANCE
    p2 = tank_v + d/2 - d.normalize().rotate(PI/2) * SHIFT_DISTANCE
    return [(p1.x, p1.y, pos[2] + " $L"),
            (p2.x, p2.y, pos[2] + " $R")]


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