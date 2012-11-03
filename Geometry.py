import numbers
from math import fabs, sqrt, pi as PI, sin, cos, copysign

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
        return Vector(
            -self.y * sin(angle) + self.x * cos(angle),
            self.y * cos(angle) + self.x * sin(angle)
        )

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return self + other * (-1)

    def __mul__(self, other):
        if issubclass(type(other), numbers.Number):
            return Vector(self.x * other, self.y * other)
        raise("WTF man?")

    def __str__(self):
        return 'Vector(%.2f, %.2f)' % (self.x, self.y)

    def __eq__(self, other):
        return numerically_zero(self.x - other.x) and numerically_zero(self.y - other.y)

    __rmul__ = __mul__

    def __truediv__(self, other):
        if issubclass(type(other), numbers.Number):
            return self.__mul__(1/other)
        raise("WTF man?")

    def length(self):
        return sqrt(self.x**2 + self.y**2)

    def normalize(self):
        return self / self.length()

    def scalar_product(self, other):
        return self.x * other.x + self.y * other.y

    def cross_product(self, other):
        return self.x * other.y - self.y * other.x

if __name__ == "__main__":
    print('Test')
    print(Vector(1, 0).rotate(7*PI/4) == Vector(sqrt(2)/2, -sqrt(2)/2))
    print(Vector(2, 0).normalize())