from math import *

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


# x_size - width
# y_size - height
def ind2sub(ind, x_size, y_size):
    x = int(floor(ind / y_size))
    y = int(ind - x * y_size)
    assert (x < x_size and y < y_size)
    return x, y


def sub2ind_tile(tile, x_size, y_size):
    return sub2ind(tile[0], tile[1], x_size, y_size)


# x_size - width
# y_size - height
def sub2ind(x, y, x_size, y_size):
    assert (x < x_size and y < y_size)
    return x * y_size + y


def sign(a):
    return (a > 0) - (a < 0)


def euclid_dist(v, u):
    return sqrt((v[0] - u[0])**2 + (v[1] - u[1])**2)


def get_tile_center(tile, game):
    return [(tile[0] + 0.5) * game.track_tile_size, (tile[1] + 0.5) * game.track_tile_size]


def tileTypeToStr(t):
    if t == TileType.LEFT_TOP_CORNER:
        return "LEFT_TOP_CORNER"
    if t == TileType.RIGHT_TOP_CORNER:
        return "RIGHT_TOP_CORNER"
    if t == TileType.LEFT_BOTTOM_CORNER:
        return "LEFT_BOTTOM_CORNER"
    if t == TileType.RIGHT_BOTTOM_CORNER:
        return "RIGHT_BOTTOM_CORNER"