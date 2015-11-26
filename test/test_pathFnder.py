from unittest import TestCase
from MockWorld import MockWorld
import PathFinder
from utils import *
from math_ex import *
from PathTile import PathTile
from DirectionExt import DirectionExt
__author__ = 'artem'


class TestPathFinder(TestCase):
    def test_find_path(self):
        mock_world = MockWorld.create('map04')
        x_size = mock_world.width
        y_size = mock_world.height
        # print [sub2ind_tile(waypoints[i], x_size, y_size) for i in xrange(len(waypoints))]

        graph = PathFinder.create_graph(mock_world.tiles_x_y, x_size, y_size)
        path_tiles = PathFinder.find_full_opt_path(graph, mock_world.waypoints, x_size, y_size)
        self.assertEqual(len(path_tiles), 66)
        self.assertEqual(path_tiles[28], PathTile((0, 0), True, 2, DirectionExt.RIGHT, 28))
        self.assertEqual(path_tiles[29], PathTile((1, 0), False, None, DirectionExt.RIGHT, 29))
        self.assertEqual(path_tiles[30], PathTile((2, 0), True, 3, DirectionExt.DOWN, 30))

