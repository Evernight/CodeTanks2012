from math import fabs

class PositionEstimator:
    context = None

def ring_linear_bonus(r, width, max_value, distance):
    return max(0, (1 - fabs(distance - r)/width)) * max_value