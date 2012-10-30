from math import pi as PI, fabs

def estimate_time_to_position(x, y, tank):
    return tank.get_distance_to(x, y) + tank.get_angle_to(x, y) / PI * 180 * 5

def move_to_position(x, y, tank, move):
    angle = tank.get_angle_to(x, y)

    def get_values(angle):
        if angle < PI/3 and tank.get_distance_to(x, y) > 400:
            left, right = 1, 1 - 2 * angle / PI
        elif angle > PI/6:
            left, right = 0.75, -1
        else:
            left, right = 1, 1 - 2 * angle / PI

        return left, right

    if angle > 0:
        move.left_track_power, move.right_track_power = get_values(fabs(angle))
    else:
        move.right_track_power, move.left_track_power = get_values(fabs(angle))
