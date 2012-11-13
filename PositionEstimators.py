from math import sqrt, fabs

class PositionEstimator:
    context = None


class StoppingPenaltyEstimator(PositionEstimator):
    # TODO: relate to bonus
    def value(self, pos):
        stopping_penalty = (1 + 2 * max(0, 100 - self.context.tank.get_distance_to(pos.x, pos.y)))**1.2
        #if bonus_summand != 0:
        #    stopping_penalty = 0
        return stopping_penalty

def ring_linear_bonus(r, width, max_value, distance):
    return max(0, (1 - fabs(distance - r)/width)) * max_value