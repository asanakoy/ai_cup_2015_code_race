__author__ = 'artem'

from model.TileType import TileType
from math import *
from collections import deque
from pprint import pprint


class TurnType:
    NONE = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3
    TOP = 4


def find_path(graph, s, end_point):
    n = len(graph)
    q = deque()
    q.appendleft(s)
    visited = n * [False]
    parent = n * [False]
    d = n * [0]
    visited[s] = True
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



    turn_matrix = [y_size * [0] for _ in range(x_size)]

    check_points = []
    check_points_indices_set = set()
    graph = create_graph(tiles_x_y, x_size, y_size)

    for i in range(len(waypoints)):
        if i < len(waypoints) - 1:
            next_wp_index = i + 1
        else:
            next_wp_index = 0
        path = find_path(graph, sub2ind(waypoints[i][0], waypoints[i][1], x_size, y_size),
                         sub2ind(waypoints[next_wp_index][0], waypoints[next_wp_index][1], x_size, y_size))

        cps = []
        for k in xrange(len(path)):
            tile = ind2sub(path[k], x_size, y_size)
            prev_ind = path[k - 1] if k > 0 else None
            next_ind = path[k + 1] if k < len(path) - 1 else None

            if prev_ind is not None and next_ind is not None:
                prev_tile = ind2sub(prev_ind, x_size, y_size)
                next_tile = ind2sub(next_ind, x_size, y_size)
                x_diff = abs(prev_tile[0] - next_tile[0])
                y_diff = abs(prev_tile[1] - next_tile[1])
                if x_diff and y_diff:  # means change driving direction
                    if prev_ind not in check_points_indices_set:
                        check_points_indices_set.add(prev_ind)
                        cps.append(prev_tile)

                    if path[k] not in check_points_indices_set:
                        check_points_indices_set.add(path[k])
                        cps.append(tile)
                        turn_matrix[tile[0]][tile[1]] = 1

                    if next_ind not in check_points_indices_set:
                        check_points_indices_set.add(next_ind)
                        cps.append(next_tile)

            elif list(tile) in waypoints and path[k] not in check_points_indices_set:
                check_points_indices_set.add(path[k])
                cps.append(tile)
                # not assigned turn_matrix[tile[0]][tile[1]] = 1
                # TODO check all waypoints on having turns and mark them

        if check_points and cps and check_points[-1] == cps[0]:
            del check_points[-1]

        check_points = check_points + cps

    assert(len(check_points) > 1)
    # assert(check_points[0] == check_points[-1])
    # del check_points[-1]

    return check_points, turn_matrix


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


if __name__ == "__main__":
    check_points, turn_matrix = find_path_test()
    pprint(check_points)
    pprint(turn_matrix)