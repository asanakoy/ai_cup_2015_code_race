from unittest import TestCase
from MockWorld import MockWorld
from MockCar import MockCar
from MockGame import MockGame
from MyCar import MyCar
from Navigator import Navigator
__author__ = 'artem'


class TestNavigator(TestCase):

    def test_update_state(self):
        mock_world = MockWorld.create('map04')
        mock_game = MockGame()
        navigator = Navigator(mock_world)
        self.assertFalse(navigator.pathfinder is None)
        self.assertFalse(navigator.pathfinder.graph is None)
        self.assertEqual(len(navigator.pathfinder.graph),
                         mock_world.height * mock_world.width)
        self.assertFalse(navigator.is_on_extra_path)

        mock_car = MockCar()
        mock_car.x = 10800
        mock_car.y = 12400
        mock_car.next_waypoint_index = 1
        car = MyCar(mock_car, mock_game.track_tile_size)
        navigator.update_state(car)
        anchor_point = navigator.get_anchor_point(car, mock_world, mock_game)
        self.assertEqual(anchor_point, (600.0, 12600.0))
        self.assertEqual(navigator._prev_path_tile_idx, 0)
        self.assertFalse(navigator.is_on_extra_path)

        mock_car.x = 10000
        mock_car.y = 12400
        mock_car.next_waypoint_index = 1
        car = MyCar(mock_car, mock_game.track_tile_size)
        navigator.update_state(car)
        self.assertEqual(navigator._prev_path_tile_idx, 1)
        self.assertFalse(navigator.is_on_extra_path)

        mock_car.x = 9200
        mock_car.y = 12400
        mock_car.next_waypoint_index = 1
        car = MyCar(mock_car, mock_game.track_tile_size)
        navigator.update_state(car)
        self.assertEqual(navigator._prev_path_tile_idx, 2)
        self.assertFalse(navigator.is_on_extra_path)

        mock_car.x = 2000
        mock_car.y = 12400
        mock_car.next_waypoint_index = 1
        car = MyCar(mock_car, mock_game.track_tile_size)
        navigator.update_state(car)
        self.assertEqual(navigator._prev_path_tile_idx, 11)
        self.assertFalse(navigator.is_on_extra_path)

        mock_car.x = 1200
        mock_car.y = 12400
        mock_car.next_waypoint_index = 2
        car = MyCar(mock_car, mock_game.track_tile_size)
        self.assertEqual(car.cur_tile, (1, 15))
        navigator.update_state(car)
        self.assertFalse(navigator.is_on_extra_path)
        self.assertEqual(navigator._prev_path_tile_idx, 12)

        mock_car.x = 1200
        mock_car.y = 11600
        mock_car.next_waypoint_index = 2
        car = MyCar(mock_car, mock_game.track_tile_size)
        self.assertEqual(car.cur_tile, (1, 14))
        navigator.update_state(car)
        self.assertTrue(navigator.is_on_extra_path)
        self.assertEqual(navigator._prev_path_tile_idx, 13)


