from math import pi as PI, fabs, degrees, sqrt
from Geometry import Vector, sign

SHELL_VELOCITY = 14
BACKWARDS_THRESHOLD = 3 * PI / 5

TIME_ESTIMATION_ANGLE_PENALTY = 5
TIME_ESTIMATION_VELOCITY_FACTOR = 20

def distance(c1, c2):
    return sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)

def estimate_time_to_position(x, y, tank):
    r = min(tank.width, tank.height)/2

    if tank.get_distance_to(x, y) < r:
        return 0
    angle = fabs(tank.get_angle_to(x, y))
    if angle > 3 * PI / 5:
        angle = PI - angle

    next_pt = (tank.x + tank.speedX * TIME_ESTIMATION_VELOCITY_FACTOR,
               tank.y + tank.speedY * TIME_ESTIMATION_VELOCITY_FACTOR)

    return distance(next_pt, (x, y)) + degrees(angle) * TIME_ESTIMATION_ANGLE_PENALTY

def estimate_target_position(target, tank):
    coord = (target.x, target.y)
    for i in range(4):
        t = tank.get_distance_to(coord[0], coord[1]) / SHELL_VELOCITY
        coord = (target.x + target.speedX * t, target.y + target.speedY * t)
        #t = tank.get_distance_to_unit(target) / SHELL_VELOCITY
    return coord

def move_to_position(x, y, tank, move):
    # TODO:
    # * pick bonuses with rectangle, not only with center
    # * smoother moves
    angle = tank.get_angle_to(x, y)

    def get_values(angle, multiplier=1):
        #ACCELERATION_REDUCTION_DISTANCE = 300
        #angle *= min(1, (ACCELERATION_REDUCTION_DISTANCE - tank.get_distance_to(x, y))/ACCELERATION_REDUCTION_DISTANCE)
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

    if fabs(angle) < BACKWARDS_THRESHOLD and tank.get_distance_to(x, y) < 500:
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