__author__ = 'artem'

from model.TileType import TileType
from math import *
from collections import deque
from pprint import pprint
from model.Direction import Direction


def find_path(graph, s, prev, end_point):
    n = len(graph)
    q = deque()
    q.appendleft(s)
    visited = n * [False]
    parent = n * [False]
    d = n * [0]
    visited[s] = True
    if prev != -1:
        visited[prev] = True

    parent[s] = -1

    end_found = False

    while q:
        v = q.pop()
        for to in graph[v]:
            if not visited[to]:
                visited[to] = True
                q.appendleft(to)
                d[to] = d[v] + 1
                parent[to] = v
                if to == end_point:
                    end_found = True
                    break
        if end_found:
            break

    assert end_found
    path = []
    v = end_point
    while v != -1:
        path.append(v)
        v = parent[v]
    path.reverse()
    return path


def find_check_points(tiles_x_y, waypoints, x_size, y_size):
    if len(waypoints) < 2:
        print 'WARNING! len(waypoints) < 2 (=%d)' % len(waypoints)
        return waypoints

    tmp = [tuple(f) for f in waypoints]
    if len(tmp) < len(set(tmp)):
        print 'WARNING! waypoints are not unique!' % len(waypoints)



    # turn_matrix = [y_size * [0] for _ in range(x_size)]

    check_points = []
    check_points_indices_set = set()
    graph = create_graph(tiles_x_y, x_size, y_size)

    for i in range(len(waypoints)):
        if i < len(waypoints) - 1:
            next_wp_index = i + 1
        else:
            next_wp_index = 0
        prev = -1
        if check_points:
            if list(waypoints[i]) != list(check_points[-1]):
                prev = sub2ind(check_points[-1][0], check_points[-1][1], x_size, y_size)
            elif len(check_points) > 1:
                prev = sub2ind(check_points[-2][0], check_points[-2][1], x_size, y_size)

        path = find_path(graph, sub2ind(waypoints[i][0], waypoints[i][1], x_size, y_size), prev,
                         sub2ind(waypoints[next_wp_index][0], waypoints[next_wp_index][1], x_size, y_size))

        cps = []
        for k in xrange(len(path)):
            tile = ind2sub(path[k], x_size, y_size)
            prev_ind = path[k - 1] if k > 0 else None
            next_ind = path[k + 1] if k < len(path) - 1 else None

            if prev_ind is not None:
                prev_tile = ind2sub(prev_ind, x_size, y_size)
            if next_ind is not None:
                next_tile = ind2sub(next_ind, x_size, y_size)

            if prev_ind is not None and next_ind is not None: # point in the middle
                x_diff = abs(prev_tile[0] - next_tile[0])
                y_diff = abs(prev_tile[1] - next_tile[1])
                if (x_diff and y_diff) or list(tile) in waypoints:  # means change driving direction or wp in the middle of path
                    if not cps or cps[-1] != tile:
                        cps.append(tile)  # could repeat
            elif list(tile) in waypoints:  #first or last point in path (it is always wp)
                if not cps or cps[-1] != tile:
                    cps.append(tile)

        if check_points and cps and check_points[-1] == cps[0]:
            del check_points[-1]

        check_points = check_points + cps

    assert(len(check_points) > 1)
    # assert(check_points[0] == check_points[-1])
    # del check_points[-1]
    if check_points[0] == check_points[-1]:
        del check_points[-1]

    check_points_directions = calculate_check_points_directions(check_points)

    return check_points, check_points_directions


UNKNOWN_DIRECTION = -1

def direction_to_str(direction):
    if direction == Direction.LEFT:
        return 'LEFT'
    elif direction == Direction.RIGHT:
        return 'RIGHT'
    elif direction == Direction.DOWN:
        return 'DOWN'
    elif direction == Direction.UP:
        return 'UP'
    else:
        return 'UNKNOWN'


def get_direction_by_vector(vector):
    if vector == [-1, 0]:
        return Direction.LEFT
    elif vector == [1, 0]:
        return Direction.RIGHT
    elif vector == [0, 1]:
        return Direction.DOWN
    elif vector == [0, -1]:
        return Direction.UP
    else:
        return UNKNOWN_DIRECTION


def get_vector_by_direction(direction):
    if direction == Direction.LEFT:
        return [-1, 0]
    elif direction == Direction.RIGHT:
        return [1, 0]
    elif direction == Direction.DOWN:
        return [0, 1]
    elif direction == Direction.UP:
        return [0, -1]
    else:
        return [0, 0]  # UNKNOWN_DIRECTION


def calculate_check_points_directions(check_points):
    directions = len(check_points) * [-1]
    for i in xrange(len(check_points)):
        next = check_points[i + 1 if i < len(check_points) - 1 else 0]
        vector = map(lambda x, y: sign(x - y), next, check_points[i])
        directions[i] = get_direction_by_vector(vector)
    return directions





def find_path_test():
    tiles_x_y = [[3, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 5],
                 [2, 4, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 9],
                 [4, 8, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 8, 5, 2],
                 [0, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 6, 2, 2],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 6, 2],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 7, 5, 2],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 2],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 8, 9, 2],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 9, 2],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 9, 2],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 6, 2],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 6, 0, 2],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 3, 6],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 1, 6, 0]]
    waypoints = [[13, 15], [1, 15], [0, 0], [2, 0], [2, 14], [13, 13]]
    x_size = 16
    y_size = 16
    return find_check_points(tiles_x_y, waypoints, x_size, y_size)



def create_graph(tiles_x_y, x_size, y_size):
    g = [[] for _ in xrange(x_size * y_size)]

    for x in xrange(x_size):
        for y in xrange(y_size):
            ind = sub2ind(x, y, x_size, y_size)
            if tiles_x_y[x][y] == TileType.VERTICAL:
                g[ind].append(sub2ind(x, y-1, x_size, y_size))
                g[ind].append(sub2ind(x, y+1, x_size, y_size))
            elif tiles_x_y[x][y] == TileType.HORIZONTAL:
                g[ind].append(sub2ind(x-1, y, x_size, y_size))
                g[ind].append(sub2ind(x+1, y, x_size, y_size))
            elif tiles_x_y[x][y] == TileType.LEFT_TOP_CORNER:
                g[ind].append(sub2ind(x+1, y, x_size, y_size))
                g[ind].append(sub2ind(x, y+1, x_size, y_size))
            elif tiles_x_y[x][y] == TileType.RIGHT_TOP_CORNER:
                g[ind].append(sub2ind(x-1, y, x_size, y_size))
                g[ind].append(sub2ind(x, y+1, x_size, y_size))
            elif tiles_x_y[x][y] == TileType.LEFT_BOTTOM_CORNER:
                g[ind].append(sub2ind(x, y-1, x_size, y_size))
                g[ind].append(sub2ind(x+1, y, x_size, y_size))
            elif tiles_x_y[x][y] == TileType.RIGHT_BOTTOM_CORNER:
                g[ind].append(sub2ind(x, y-1, x_size, y_size))
                g[ind].append(sub2ind(x-1, y, x_size, y_size))
            elif tiles_x_y[x][y] == TileType.LEFT_HEADED_T:
                g[ind].append(sub2ind(x, y-1, x_size, y_size))
                g[ind].append(sub2ind(x, y+1, x_size, y_size))
                g[ind].append(sub2ind(x-1, y, x_size, y_size))
            elif tiles_x_y[x][y] == TileType.RIGHT_HEADED_T:
                g[ind].append(sub2ind(x, y-1, x_size, y_size))
                g[ind].append(sub2ind(x, y+1, x_size, y_size))
                g[ind].append(sub2ind(x+1, y, x_size, y_size))
            elif tiles_x_y[x][y] == TileType.TOP_HEADED_T:
                g[ind].append(sub2ind(x-1, y, x_size, y_size))
                g[ind].append(sub2ind(x+1, y, x_size, y_size))
                g[ind].append(sub2ind(x, y-1, x_size, y_size))
            elif tiles_x_y[x][y] == TileType.BOTTOM_HEADED_T:
                g[ind].append(sub2ind(x-1, y, x_size, y_size))
                g[ind].append(sub2ind(x+1, y, x_size, y_size))
                g[ind].append(sub2ind(x, y+1, x_size, y_size))
            elif tiles_x_y[x][y] == TileType.CROSSROADS:
                g[ind].append(sub2ind(x-1, y, x_size, y_size))
                g[ind].append(sub2ind(x+1, y, x_size, y_size))
                g[ind].append(sub2ind(x, y-1, x_size, y_size))
                g[ind].append(sub2ind(x, y+1, x_size, y_size))
    return g


#x_size - width
#y_size - height
def ind2sub(ind, x_size, y_size):
    x = int(floor(ind / y_size))
    y = int(ind - x * y_size)
    assert (x < x_size and y < y_size)
    return x, y

#x_size - width
#y_size - height
def sub2ind(x, y, x_size, y_size):
    assert (x < x_size and y < y_size)
    return x * y_size + y


def sign(a):
    return (a > 0) - (a < 0)

def euclid_dist(v, u):
    return sqrt((v[0] - u[0])**2 + (v[1] - u[1])**2)


def get_tile_center(tile, game):
    return [(tile[0] + 0.5) * game.track_tile_size, (tile[1] + 0.5) * game.track_tile_size]


if __name__ == "__main__":
    check_points, directions = find_path_test()
    pprint(check_points)
    pprint(map(lambda d: direction_to_str(d), directions))

