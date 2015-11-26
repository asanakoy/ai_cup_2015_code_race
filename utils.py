from math import *
from model.Move import Move

__author__ = 'artem'


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


def tileTypeToStr(t):
    if t == TileType.LEFT_TOP_CORNER:
        return "LEFT_TOP_CORNER"
    if t == TileType.RIGHT_TOP_CORNER:
        return "RIGHT_TOP_CORNER"
    if t == TileType.LEFT_BOTTOM_CORNER:
        return "LEFT_BOTTOM_CORNER"
    if t == TileType.RIGHT_BOTTOM_CORNER:
        return "RIGHT_BOTTOM_CORNER"

def move_to_str(move):
    """
    :type move: Move
    """
    return 'MOVE: EP(%d) BRAKE(%d), SHOOT(%d), OIL(%d), WT(%.16f)' % (move.engine_power,
         move.brake, move.throw_projectile, move.spill_oil, move.wheel_turn)
