import numbers
from math import fabs, sqrt, pi as PI, sin, cos, copysign, acos, hypot

EPSILON_ERROR = 1e-9

def numerically_zero(x):
    return fabs(x) < EPSILON_ERROR

def sign(x):
    return copysign(1, x)

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def rotate(self, angle):
        s, c = sin(angle), cos(angle)
        return Vector(
            -self.y * s + self.x * c,
            self.y * c + self.x * s
        )

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Vector(self.x * other, self.y * other)

    def __str__(self):
        return 'Vector(%.2f, %.2f)' % (self.x, self.y)

    def __eq__(self, other):
        return numerically_zero(self.x - other.x) and numerically_zero(self.y - other.y)

    __rmul__ = __mul__

    def __truediv__(self, other):
        #if issubclass(type(other), numbers.Number):
        #    return self.__mul__(1/other)
        return self.__mul__(1/other)
        #raise("WTF man?")

    def length(self):
        return hypot(self.x, self.y)

    def normalize(self):
        return self / self.length()

    def scalar_product(self, other):
        return self.x * other.x + self.y * other.y

    def cross_product(self, other):
        return self.x * other.y - self.y * other.x

    def projection(self, other):
        return self.scalar_product(other)/other.length()

    def angle(self, other):
        c = self.normalize().scalar_product(other.normalize())
        c = max(-1, min(c, 1))
        return acos(c)

    def is_zero(self):
        return numerically_zero(self.x) and numerically_zero(self.y)

    def distance_to_line(self, x, d):
        a = (self - x).scalar_product(d)/d.scalar_product(d)
        return ((x - self) + a * d).length()

    def distance(self, v):
        return (self - v).length()

    def collinear(self, v):
        return numerically_zero(self.cross_product(v))

def get_unit_corners(unit):
    a = unit.angle
    center = Vector(unit.x, unit.y)

    c1 = center + Vector(unit.width/2, unit.height/2).rotate(a)
    c2 = center + Vector(unit.width/2, -unit.height/2).rotate(a)
    c3 = center + Vector(-unit.width/2, -unit.height/2).rotate(a)
    c4 = center + Vector(-unit.width/2, unit.height/2).rotate(a)

    return [c1, c2, c3, c4]

def ordered_points(c, p1, p2, p3):
    v1 = p1 - c
    v2 = p2 - c
    v3 = p3 - c
    return sign(v1.cross_product(v2)) == sign(v2.cross_product(v3))

def segments_are_intersecting(p1, p2, q1, q2):
    return (
        ordered_points(p1, q1, p2, q2) and
        ordered_points(p2, q1, p1, q2) and
        ordered_points(q1, p1, q2, p2) and
        ordered_points(q2, p1, q1, p2))

def intersect_lines(p, a, q, b):
    z = q - p
    ab = a.cross_product(b)
    return (z.cross_product(b)/ab, z.cross_product(a)/ab)

if __name__ == "__main__":
    print('Test')
    print(Vector(1, 0).rotate(7*PI/4) == Vector(sqrt(2)/2, -sqrt(2)/2))
    print(Vector(2, 0).normalize())

    print(segments_are_intersecting(
        Vector(0, 0),
        Vector(5, 5),
        Vector(0, 1),
        Vector(-6, -2),
    ))

    print(intersect_lines(
        Vector(0, 0),
        Vector(-0.5, 0),
        Vector(5, 5),
        Vector(0, -1)
    ))