from math import pi as PI, fabs, degrees, sqrt
from Geometry import Vector, sign, numerically_zero

SHELL_VELOCITY = 14
SHELL_ACCELERATION = -0.08
INITIAL_SHELL_VELOCITY = 16.58333316713906

BACKWARDS_THRESHOLD = 2 * PI / 3
TARGET_REACHED_DISTANCE = 30
DISTANCE_EPSILON = 1

def distance(c1, c2):
    return sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)

def distance_to_edge(x, y, world):
    return min(x, world.width - x, y, world.height - y)

TIME_ESTIMATION_ANGLE_PENALTY = 30
TIME_ESTIMATION_VELOCITY_FACTOR = 20
def estimate_time_to_position(x, y, tank):
    return 0

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

    def get_values(angle, multiplier=1):
        #if fabs(angle) < PI/6 and fabs(tank.angular_speed) < 0.02:
        #    left, right = 1, 1
        #else:
        #    left, right = 1, -1
        if tank.get_distance_to(x, y) < 300:
            left, right = 1, 1 - 6 * angle / PI
        elif tank.get_distance_to(x, y) < 700:
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

    if fabs(angle) < BACKWARDS_THRESHOLD or tank.get_distance_to(x, y) > 500:
        if angle > 0:
            move.left_track_power, move.right_track_power = get_values(fabs(angle))
        else:
            move.right_track_power, move.left_track_power = get_values(fabs(angle))
    else:
        if angle > 0:
            move.left_track_power, move.right_track_power = get_values(PI - fabs(angle), -1)
        else:
            move.right_track_power, move.left_track_power = get_values(PI - fabs(angle), -1)

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

def attacked_area(x, y, enemy):
    """
    Rectangle shape
    """
    DANGEROUS_WIDTH = 80

    pt_v = Vector(x, y)
    enemy_v = Vector(enemy.x, enemy.y)
    turret_v = Vector(1, 0).rotate(enemy.angle + enemy.turret_relative_angle)
    if (pt_v - enemy_v).scalar_product(turret_v) <= 0:
        return 0

    td = turret_v.rotate(PI/2) * DANGEROUS_WIDTH
    p1 = enemy_v + td
    p2 = enemy_v - td
    if sign(turret_v.cross_product(pt_v - p1)) == sign(turret_v.cross_product(pt_v - p2)):
        return 0
    else:
        return 1

def shell_will_hit_tank_going_to(shell, tank, x, y):
    """
    WTF is written here???
    """
    tank_v = Vector(tank.x, tank.y)
    shell_v = Vector(shell.x, shell.y)
    pt_v = Vector(x, y)
    vt = pt_v - tank_v
    vs = Vector(shell.speedX, shell.speedY)
    if vs == vt:
        return False

    r = tank_v - shell_v
    w = vs - vt
    if not numerically_zero(w.x):
        t = r.x/w.x
    else:
        t = r.y/w.y
    if t < 0:
        return False

    meeting = tank_v + vt * t
    if t < 70:
        return True
    return False

def solve_quadratic(a, b, c):
    D = b*b - 4 * a * c
    r1, r2 = (-b + sqrt(D))/(2 * a), (-b - sqrt(D))/(2 * a)
    if r1 > 0:
        return r1
    else:
        return r2