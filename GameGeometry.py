from math import pi as PI, fabs, degrees, sqrt

SHELL_VELOCITY = 15
BACKWARDS_THRESHOLD = 3 * PI / 5

def distance(c1, c2):
    return sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)

def estimate_time_to_position(x, y, tank):
    angle = fabs(tank.get_angle_to(x, y))
    if angle > 3 * PI / 5:
        angle = PI - angle
    return tank.get_distance_to(x, y) + degrees(angle) * 7

def estimate_target_position(target, tank):
    t = tank.get_distance_to_unit(target) / SHELL_VELOCITY
    return (target.x + target.speedX * t, target.y + target.speedY * t)

def move_to_position(x, y, tank, move):
    # TODO:
    # * pick bonuses with rectangle, not only with center
    # * smoother moves
    angle = tank.get_angle_to(x, y)

    def get_values(angle, multiplier=1):
        if angle < PI/3 and tank.get_distance_to(x, y) > 500:
            # Long-run distance
            left, right = 1, 1 - 1.75 * angle / PI
        elif tank.get_distance_to(x, y) < 50:
            # Dirty fix for picking up close bonuses
            left, right = 1, 1 - 2 * angle / PI
        elif angle > PI/6:
            # Big angle
            left, right = 0.75, -1
        else:
            left, right = 1, 1

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
