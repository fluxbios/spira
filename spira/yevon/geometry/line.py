import numpy as np

from spira.core.initializer import FieldInitializer
from spira.core.transformable import Transformable
from spira.core.param.variables import NumberField
from spira.core.descriptor import DataFieldDescriptor
from spira.yevon.geometry.coord import Coord


__all__ = [
    'Line',
    'LineField',
    'line_from_point_angle',
    'line_from_slope_intercept',
    'line_from_two_points',
    'line_from_vector'
]


DEG2RAD = np.pi/180
RAD2DEG = 180/np.pi


class Line(Transformable, FieldInitializer):
    """ Creates a line ax + by + c = 0. """

    a = NumberField(default=1)
    b = NumberField(default=1)
    c = NumberField(default=1)

    def __init__(self, a, b, c, **kwargs):
        super().__init__(a=a, b=b, c=c, **kwargs)

    def __repr__(self):
        return "[SPiRA: Line] ({}x {}y + {})".format(self.a, self.b, self.c)

    def __str__(self):
        return self.__repr__()

    @property
    def slope(self):
        if self.b == 0:
            return None
        return -self.a / self.b

    @property
    def angle_rad(self):
        return np.arctan2(-self.a, self.b)

    @property
    def angle_deg(self):
        return RAD2DEG * self.angle_rad

    @property
    def y_intercept(self):
        if self.b == 0.0:
            return None
        return -self.c / -self.b

    @property
    def x_intercept(self):
        if self.a == 0.0:
            return None
        return -self.c / -self.a

    def is_on_line(self, coordinate):
        return abs(self.a * coordinate[0] + self.b * coordinate[1] + self.c) < 1e-10

    def distance(self, coordinate):
        return abs(self.a * coordinate[0] + self.b * coordinate[1] + self.c) / np.sqrt(self.a ** 2 + self.b ** 2)

    def get_coord_from_distance(self, destination, distance):
        d = distance
        m = self.slope
        x0 = destination.midpoint[0]
        y0 = destination.midpoint[1]

        if m is None:
            dx, dy = 0, distance
        else:
            angle = self.angle_deg
            angle = np.mod(angle, 360)
            if 90 < angle <= 270:
                x = x0 + d / np.sqrt(1 + m**2)
            elif (0 < angle <= 90) or (270 < angle <= 360):
                x = x0 - d / np.sqrt(1 + m**2)
            else:
                raise ValueError('Angle {} not accepted.'.format(angle))
            y = m*(x - x0) + y0
            dx = x - x0
            dy = y - y0
    
        return (dx, dy)

    def intersection(self, line):
        """ gives intersection of line with other line """
        if (self.b * line.a - self.a * line.b) == 0.0:
            return None
        return Coord(-(self.b * line.c - line.b * self.c) / (self.b * line.a - self.a * line.b),
                      (self.a * line.c - line.a * self.c) / (self.b * line.a - self.a * line.b))

    def closest_point(self, point):
        """ Gives closest point on line """
        line2 = straight_line_from_point_angle(point, self.angle_deg + 90.0)
        return self.intersection(line2)

    def is_on_same_side(self, point1, point2):
        """ Returns True is both points are on the same side of the line """
        return numpy.sign(self.a * point1[0] + self.b * point1[1] + self.c) == np.sign(self.a * point2[0] + self.b * point2[1] + self.c)

    def is_parallel(self, other):
        """ Returns True is lines are parallel """
        return abs(self.a * other.b - self.b * other.a) < 1E-10

    def __eq__(self, other):
        return abs(self.a * other.b - self.b * other.a) < 1E-10 and abs(self.c * other.b - self.b * other.c) < 1E-10 and abs(self.a * other.c - self.c * other.a) < 1E-10    
        
    def __ne__(self, other):
        return (not self.__eq__(other))    
    
    def __get_2_points__(self):
        """ Returns 2 points on the line. If a horizontal or vertical, it returns one point on the axis, and another 1.0 further.
            If the line is oblique, it returns the intersects with the axes """
        from .shape import Shape
        if b == 0:
            return Shape([Coord(-self.c / self.a, 0.0), Coord(-self.c / self.a, 1.0)])
        elif a == 0: 
            return Shape([Coord(0.0, -self.c / self.b), Coord(1.0, -self.c / self.b)])
        else:
            return Shape([Coord(-self.c / self.a, 0.0), Coord(0.0, -self.c / self.b)])
    
    def transform(self, transformation):
        """ transforms the straight line with a given transformation """
        p = self.__get_2_points__().transform(transformation)
        self.a = y2 - y1
        self.b = x1 - x2
        self.c = (x2 - x1) * y1 - (y2 - y1) * x1
        
    def transform_copy(self, transformation):
        """ transforms a copy of the straight line with a given transformation """
        p = self.__get_2_points__().transform(transformation)
        return line_from_two_points(p[0], p[1])


def line_from_slope_intercept(slope, y_intercept):
    """ creates StraightLine object from slope and y_intercept """
    return Line(slope, -1.0, intercept)


def line_from_two_points(point1, point2):
    """ creates StraightLine object from two points """
    x1, y1 = point1[0], point1[1]
    x2, y2 = point2[0], point2[1]
    return Line(y2 - y1, x1 - x2, (x2 - x1) * y1 - (y2 - y1) * x1)


def line_from_point_angle(point, angle):
    """ Creates StraightLine object from point and angle. """
    if abs(angle % 180.0 - 90.0) <= 1e-12:
        return line_from_two_points(point, Coord(0.0, 1) + point)
    slope = np.tan(DEG2RAD * angle)
    return Line(slope, -1, point[1] - slope * point[0])


def line_from_vector(vector):
    """ creates StraightLine object from a vector """
    return line_from_point_angle(vector.position, vector.angle_deg)


def LineField(restriction=None, preprocess=None, **kwargs):
    if 'default' not in kwargs:
        kwargs['default'] = Line()
    R = RestrictType(Line) & restriction
    return DataFieldDescriptor(restrictions=R, **kwargs)
