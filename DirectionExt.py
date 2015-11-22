__author__ = 'artem'

from model.Direction import Direction

class DirectionExt(Direction):
    UNKNOWN = None


def direction_to_str(direction):
    if direction == Direction.LEFT:
        return 'LEFT'
    elif direction == Direction.RIGHT:
        return 'RIGHT'
    elif direction == Direction.DOWN:
        return 'DOWN'
    elif direction == Direction.UP:
        return 'UP'
    elif direction == DirectionExt.UNKNOWN:
        return 'UNKNOWN'
    else:
        raise ValueError('Unknown value')


def get_direction_by_vector(vector):
    assert type(vector) is list
    if vector == [-1, 0]:
        return Direction.LEFT
    elif vector == [1, 0]:
        return Direction.RIGHT
    elif vector == [0, 1]:
        return Direction.DOWN
    elif vector == [0, -1]:
        return Direction.UP
    else:
        return DirectionExt.UNKNOWN


def get_vector_by_direction(direction):
    if direction == Direction.LEFT:
        return [-1, 0]
    elif direction == Direction.RIGHT:
        return [1, 0]
    elif direction == Direction.DOWN:
        return [0, 1]
    elif direction == Direction.UP:
        return [0, -1]
    elif direction == DirectionExt.UNKNOWN:
        return None # UNKNOWN_DIRECTION
    else:
        raise ValueError('Unknown value')



if __name__ == '__main__':
    str = direction_to_str(DirectionExt.DOWN)
    print str

    print direction_to_str(get_direction_by_vector([-1, 0]))