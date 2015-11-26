from math import *
import numpy as np

__author__ = 'artem'


def vector_add(v1, v2):
    return tuple(map(lambda a, b: a + b, v1, v2))


def v_add_with_coeff(v1, v2, coeff1, coeff2):
    res = [0, 0]
    for i in range(2):
        res[i] = v1[i] * coeff1 + v2[i] * coeff2
    return tuple(res)


def vector_substract(v1, v2):
    return tuple(map(lambda a, b: a - b, v1, v2))


def sign(a):
    return (a > 0)*1.0 - (a < 0)*1.0


def euclid_dist(v, u):
    return sqrt((v[0] - u[0])**2 + (v[1] - u[1])**2)


def get_tile_center(tile, game):
    return [(tile[0] + 0.5) * game.track_tile_size, (tile[1] + 0.5) * game.track_tile_size]


def get_speed_projection(speed_x, speed_y, direction):
    speed_module = hypot(speed_x, speed_y)
    speed_sign = sign(direction[0] * speed_x + direction[1] * speed_y)
    return speed_sign * speed_module


def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    theta = np.asarray(theta)
    axis = axis/math.sqrt(np.dot(axis, axis))
    a = math.cos(theta/2)
    b, c, d = -axis*math.sin(theta/2)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])