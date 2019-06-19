import gdspy
import math
import pyclipper
import numpy as np
import networkx as nx

from spira.log import SPIRA_LOG as LOG
from numpy.linalg import norm
from spira.yevon import constants
from spira.yevon.geometry.coord import Coord
from spira.yevon.process import get_rule_deck


RDD = get_rule_deck()


def angle_diff(a1, a2):
    return np.round(np.abs(np.mod(a2-a1, 360)), 3)


def angle_rad(coord, origin=(0.0, 0.0)):
    """ Absolute angle (radians) of coordinate with respect to origin"""
    return math.atan2(coord[1] - origin[1], coord[0] - origin[0])


def angle_deg(coord, origin=(0.0, 0.0)):
    """ Absolute angle (radians) of coordinate with respect to origin"""
    return angle_rad(coord, origin) * constants.RAD2DEG


def distance(coord, origin=(0.0, 0.0)):
    """ Distance of coordinate to origin. """
    return np.sqrt((coord[0] - origin[0])**2 + (coord[1] - origin[1])**2)


def encloses(points, position):
    assert position is not None, 'No label position found.'
    if pyclipper.PointInPolygon(position, points) != 0:
        return True
    return False


def snap_points(points, grids_per_unit=None):
    """ Round a list of points to a grid value. """
    if grids_per_unit is None:
        grids_per_unit = _grids_per_unit()
    else:
        raise ValueError('please define grids per unit')
    points = _points_to_float(points)
    polygons = list()
    for coords in points:
        poly = list()
        for coord in coords:
            p1 = (math.floor(coord[0] * grids_per_unit + 0.5)) / grids_per_unit
            p2 = (math.floor(coord[1] * grids_per_unit + 0.5)) / grids_per_unit
            poly.append([int(p1), int(p2)])
        polygons.append(poly)

    return polygons


def c2d(coord):
    """ Convert coordinate to 2D. """
    # pp = [(coord[i]/(RDD.GDSII.GRID)) for i in range(len(list(coord))-1)]
    pp = [coord[i] for i in range(len(list(coord))-1)]
    return pp


def c3d(coord):
    """ Convert coordinate to 3D. """
    # pp = [coord[i]*RDD.GDSII.GRID for i in range(len(list(coord)))]
    pp = [coord[i] for i in range(len(list(coord)))]
    return pp


def scale_coord_up(coord):
    return [c*constants.SCALE_UP for c in coord]


def scale_coord_down(coord):
    return [c*constants.SCALE_DOWN for c in coord]


def scale_polygon_up(polygons, value=None):
    if value is None:
        value = constants.SCALE_UP
    new_poly = []
    for points in polygons:
        pp = np.array([np.array([np.floor(float(p[0]*value)), np.floor(float(p[1]*value))]) for p in points])
        new_poly.append(pp)
    return new_poly


def scale_polygon_down(polygons, value=None):
    if value is None:
        value = constants.SCALE_DOWN
    new_poly = []
    for points in polygons:
        pp = np.array([np.array([np.floor(np.int32(p[0]*value)), np.floor(np.int32(p[1]*value))]) for p in points])
        new_poly.append(pp)
    return new_poly


def numpy_to_list(points, start_height, unit=None):
    return [[float(p[0]*unit), float(p[1]*unit), start_height] for p in points]


def cut(ply, position, axis):
    import spira.all as spira
    plys = spira.ElementalList()
    gp = ply.commit_to_gdspy()
    pl = gdspy.slice(objects=[gp], position=position, axis=axis)
    for p in pl:
        if len(p.polygons) > 0:
            plys += spira.Polygon(shape=p.polygons[0])
    return plys


def lines_cross(begin1, end1, begin2, end2, inclusive=False):
    """ Returns true if the line segments intersect """
    A1 = end1[1] - begin1[1]
    B1 = -end1[0] + begin1[0]
    C1 = - (begin1[1] * B1 + begin1[0] * A1)
    A2 = end2[1] - begin2[1]
    B2 = -end2[0] + begin2[0]
    C2 = - (begin2[1] * B2 + begin2[0] * A2)
    if A1 * B2 == A2 * B1:
        return False
    if inclusive:
        return ((A1 * begin2[0] + B1 * begin2[1] + C1) * (A1 * end2[0] + B1 * end2[1] + C1) <= 0 and
                (A2 * begin1[0] + B2 * begin1[1] + C2) * (A2 * end1[0] + B2 * end1[1] + C2) <= 0)
    else:
        return ((A1 * begin2[0] + B1 * begin2[1] + C1) * (A1 * end2[0] + B1 * end2[1] + C1) < 0 and
                (A2 * begin1[0] + B2 * begin1[1] + C2) * (A2 * end1[0] + B2 * end1[1] + C2) < 0)


def lines_coincide(begin1, end1, begin2, end2):
    """ Returns true if the line segments intersect. """
    A1 = end1[1] - begin1[1]
    B1 = -end1[0] + begin1[0]
    C1 = - (begin1[1] * B1 + begin1[0] * A1)
    A2 = end2[1] - begin2[1]
    B2 = -end2[0] + begin2[0]
    C2 = - (begin2[1] * B2 + begin2[0] * A2)
    if (not(A1 or B1)) or (not(A2 or B2)):
        return False
    return abs(A1 * B2 - A2 * B1) < 1E-10 and abs(C1 * A2 - C2 * A1) < 1E-10 and abs(C1 * B2 - C2 * B1) < 1E-10


def intersection(begin1, end1, begin2, end2):
    """ Gives the intersection between two lines (not sections). """
    A1 = end1[1] - begin1[1]
    B1 = -end1[0] + begin1[0]
    C1 = begin1[1] * B1 + begin1[0] * A1
    A2 = end2[1] - begin2[1]
    B2 = -end2[0] + begin2[0]
    C2 = begin2[1] * B2 + begin2[0] * A2
    if A1 * B2 == A2 * B1:
        LOG.error("Can't intersect parallel lines")
        raise ValueError('Cannot be parallel.')
    x = (C1 * B2 - C2 * B1) / (A1 * B2 - A2 * B1)
    y = (C1 * A2 - C2 * A1) / (B1 * A2 - B2 * A1)
    return Coord(x, y)


def sort_points_on_line(point_list):
    """ Sorts points on a line, taking the two first points as the reference direction """
    point_list = [Coord(p[0], p[1]) for p in point_list]
    p0 = point_list[0]
    dx = point_list[1][0] - point_list[0][0]
    dy = point_list[1][1] - point_list[0][1]
    point_list.sort(key=lambda p: distance(p, p0))
    return point_list


def points_unique(coordinates):
    unique_coordinates = []
    for c in coordinates:
        already_in_list = False
        for uc in unique_coordinates:
            if c == uc:
                already_in_list = True
        if not already_in_list:
            unique_coordinates.append(c)
    return unique_coordinates

                                
def distance(coord, origin=(0,0)):
    """ Distance of coordinate to origin """
    return np.sqrt((coord[0] - origin[0])**2 + (coord[1] - origin[1])**2)


