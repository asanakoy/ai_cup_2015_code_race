from utils import *
from DirectionExt import *
from PathTile import PathTile
from model.TileType import TileType
from math import *
from collections import deque
# from pprint import pprint
# from model.World import World


class PathFinder:

    def __init__(self, world):
        """
        :param world: World
        """
        self.world = world
        self.graph = create_graph(world.tiles_x_y, world.width, world.height)

    def find_path(self, start_tile, prev, end_tile):
        start_point = sub2ind_tile(start_tile, self.world.width, self.world.height)
        end_point = sub2ind_tile(end_tile, self.world.width, self.world.height)
        path = _find_path(self.graph, start_point, prev, end_point)
        return path

    def find_extra_path(self, old_path, cur_tile, next_waypoint_index):
        first_segment = self.find_path(self.world.waypoints[next_waypoint_index-1],
                                             -1, cur_tile)
        second_segment = self.find_path(cur_tile, -1,
                                           self.world.waypoints[next_waypoint_index])

        assert(first_segment[-1] == second_segment[0])
        new_path_segment = first_segment[:-1] + second_segment

        new_segment_tiles = _covert_path_to_2d(new_path_segment, self.world.waypoints,
                                               self.world.width, self.world.height, next_waypoint_index-1)
        extra_path = _merge_new_segment_into_path(old_path, new_segment_tiles)
        calculate_path_tiles_directions_and_indices(extra_path)
        extra_wp_lookup_table = _build_wp_lookup_table(extra_path)
        return extra_path, extra_wp_lookup_table


    def find_full_opt_path(self):
        tile_path = find_full_opt_path(self.graph, self.world.waypoints, self.world.width, self.world.height)
        wp_lookup_table = _build_wp_lookup_table(tile_path)
        return tile_path, wp_lookup_table


def _find_path(graph, start_point, prev, end_point):
    """
    :param graph:
    :param start_point:
    :param prev: forbidden to visit
    :param end_point:
    :return: path from start_point to end_point. Each point is linear index
    """
    # print start_point, prev, end_point
    n = len(graph)
    q = deque()
    q.appendleft(start_point)
    visited = n * [False]
    parent = n * [False]
    d = n * [0]
    visited[start_point] = True
    if prev != -1:
        visited[prev] = True

    parent[start_point] = -1

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


def find_full_opt_path(graph, waypoints, map_x_size, map_y_size):
    if len(waypoints) < 2:
        print 'WARNING! len(waypoints) < 2 (=%d)' % len(waypoints)
        return waypoints

    tmp = [tuple(f) for f in waypoints]
    if len(tmp) < len(set(tmp)):
        print 'WARNING! waypoints are not unique!' % len(waypoints)
        assert False

    path_tiles = []

    for i in range(len(waypoints)):
        if i < len(waypoints) - 1:
            next_wp_index = i + 1
        else:
            next_wp_index = 0
        prev = -1
        if path_tiles:
            if list(waypoints[i]) != list(path_tiles[-1].coord):
                prev = sub2ind(path_tiles[-1].coord[0], path_tiles[-1].coord[1], map_x_size, map_y_size)
            elif len(path_tiles) > 1:
                prev = sub2ind(path_tiles[-2].coord[0], path_tiles[-2].coord[1], map_x_size, map_y_size)

        path = _find_path(graph, sub2ind(waypoints[i][0], waypoints[i][1], map_x_size, map_y_size),
                         prev, sub2ind(waypoints[next_wp_index][0], waypoints[next_wp_index][1],
                                       map_x_size, map_y_size))

        cps = _covert_path_to_2d(path, waypoints, map_x_size, map_y_size, i)
        assert(not path_tiles or not cps or cps[0] == path_tiles[-1])

        if path_tiles and cps and path_tiles[-1] == cps[0]:
            del path_tiles[-1]

        path_tiles = path_tiles + cps

    assert(len(path_tiles) > 1)
    # assert(path_tiles[0] == path_tiles[-1])
    # del path_tiles[-1]
    if path_tiles[0] == path_tiles[-1]:
        del path_tiles[-1]

    calculate_path_tiles_directions_and_indices(path_tiles)

    return path_tiles


def _covert_path_to_2d(path, waypoints, map_x_size, map_y_size, start_wp_index=0):
    path_tiles = [PathTile((0, 0)) for _ in xrange(len(path))]
    next_wp_index = start_wp_index
    for k in xrange(len(path)):
        tile = ind2sub(path[k], map_x_size, map_y_size)
        path_tiles[k].coord = tile
        if path_tiles[k].coord == tuple(waypoints[next_wp_index]):
            path_tiles[k].is_waypoint = True
            path_tiles[k].wp_index = next_wp_index
            next_wp_index = next_wp_index + 1 if next_wp_index + 1 < len(waypoints) else 0
    assert(next_wp_index - start_wp_index <= len(waypoints))
    return path_tiles


def calculate_path_tiles_directions_and_indices(path_tiles):
    """
    :param path_tiles: list of PathTile's
    :return:
    """
    for i in xrange(len(path_tiles)):
        next_tile = path_tiles[i + 1 if i < len(path_tiles) - 1 else 0]
        vector = map(lambda x, y: sign(x - y), next_tile.coord, path_tiles[i].coord)
        path_tiles[i].direction = get_direction_by_vector(vector)
        path_tiles[i].direction_vector = tuple(vector)
        path_tiles[i].index = i


def create_graph(tiles_x_y, x_size, y_size):
    """
    :param x_size: width
    :param y_size: height
    :return: graph
    """
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


def _merge_new_segment_into_path(path, new_segment):
    """

    :type path: list of PathTile
    :param path: optimal path (the whole lap)
    :type new_segment: list of PathTile
    :param new_segment: new path segment between last wp and next wp
    :return:
    """
    assert(new_segment[0].is_waypoint == new_segment[-1].is_waypoint == True and
           new_segment[0].coord != new_segment[-1].coord)
    idx_start = 0
    while idx_start < len(path):
        if path[idx_start].is_waypoint and path[idx_start].coord == new_segment[0].coord:
            break
        else:
            idx_start += 1
    assert idx_start < len(path)

    idx_end = idx_start + 1

    while idx_end < len(path):
       if path[idx_end].is_waypoint and path[idx_end].coord == new_segment[-1].coord:
           break
       else:
           idx_end += 1
    if idx_end == len(path):
        idx_end = 0
        assert(path[idx_end].coord == new_segment[-1].coord)

    if idx_end != 0:
       new_path = path[0:idx_start] + new_segment[0:-1] + path[idx_end:]
    else:
       new_path = path[0:idx_start] + new_segment[0:-1]
    return new_path


def _build_wp_lookup_table(path):
    """
    :type path: list of PathTile
    :return:
    """
    lookup_table = []
    for i in xrange(len(path)):
        if path[i].is_waypoint:
            lookup_table.append(i)

    return lookup_table





# if __name__ == "__main__":
    # find_path_test()
    # check_points, directions = find_path_test()
    # pprint(check_points)
    # pprint(map(lambda d: direction_to_str(d), directions))

