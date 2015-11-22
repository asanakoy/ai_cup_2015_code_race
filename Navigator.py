__author__ = 'artem'

from utils import *
from DirectionExt import *
from MyCar import MyCar
import PathFinder

class Navigator:

    def __init__(self, world):
        """
        :param world: World
        """
        self._opt_path = None
        self._opt_path_wp_lookup_table = None
        self._extra_path = None
        self._extra_path_wp_lookup_table = None
        self.path = None  # Current Actual path. May be Optimal or Extra
        self.pathfinder = PathFinder.PathFinder(world)
        self.is_on_extra_path = False

        # index of previous tile (previous tick) in the current path
        # Do not use outside of update() method
        self._prev_path_tile_idx = 0
        self.cur_path_idx = None  # current tile index in the path

        self.is_on_turn = False
        self.is_turning_started = False
        self.is_turn_180_grad = False

    def _get_path(self):
        """
        :rtype: list of PathTile
        """
        if self.is_on_extra_path:
            return self._extra_path
        return self._opt_path

    # Invariant: between two waypoints int he optimal path the chain
    # is always simple (each point occurs on;y one time).
    # In extra path the chain can contain duplicate points
    def _find_tile_in_path(self, tile, last_pathtile_idx):
        assert type(tile) is tuple
        path = self._get_path()
        assert path is not None

        indices = range(last_pathtile_idx, len(path)) + [0]
        for i in indices:
            if path[i].coord == tile:
                return i
        return None

    def update_state(self, car):
        """
        Update inner state of the navigator. Must be called every tick.
        WARNING: self.path may be outdated until the end of the call update(). Use getter instead.
        @type car: MyCar
        """

        if self._opt_path is None:
            self._opt_path, self._opt_path_wp_lookup_table = self.pathfinder.find_full_opt_path()

        idx = self._find_tile_in_path(car.cur_tile, self._prev_path_tile_idx)

        # if we strayed from the path
        if idx is None:
            self._extra_path, self._extra_path_wp_lookup_table \
                = self.pathfinder.find_extra_path(self._opt_path, car.cur_tile,
                                                  car.base.next_waypoint_index)
            self.is_on_extra_path = True
            # from the prev_wp to the new extra tile chain is always simple
            idx = self._find_tile_in_path(car.cur_tile,
                                          self._extra_path_wp_lookup_table[car.base.next_waypoint_index - 1])
            self._prev_path_tile_idx = idx
            assert idx is not None

        path = self._get_path()
        if path[idx].is_waypoint and self.is_on_extra_path:
            idx = self._opt_path_wp_lookup_table[path[idx].wp_index]  # index in the _opt_path
            self.is_on_extra_path = False
            self._extra_path = None
            self._extra_path_wp_lookup_table = None

        self.path = self._get_path()
        self._prev_path_tile_idx = idx
        self.cur_path_idx = idx


    def get_anchor_point(self, car, game):
        """
        :type car: MyCar
        :type game: model.Game
        :rtype: tuple of double
        """
        DISTANCE_BEFORE_TURN = game.track_tile_size * 1.5
        self.is_turning_started = False
        self.is_turn_180_grad = False
        self.is_on_turn = self.path[self.cur_path_idx - 1].direction != self.path[self.cur_path_idx].direction
        next_turn_cp_index, dist_to_next_turn = self.find_next_turn()
        next_path_tile = self._get_path_tile(self.cur_path_idx + 1)
        next_next_path_tile = self._get_path_tile(self.cur_path_idx + 2)

        if self.is_on_turn and self.is_starts_turn_180_grad(self.cur_path_idx):
            self.is_turn_180_grad = True
        elif dist_to_next_turn == 1 and \
                next_path_tile.direction != next_next_path_tile.direction and \
                self.path[self.cur_path_idx].direction == next_next_path_tile.direction and \
                not self.is_starts_turn_180_grad(next_path_tile.index) and \
                not self.is_starts_turn_180_grad(next_next_path_tile.index):

            # going straight through sequential turns
            turn_center_point = get_tile_center(next_path_tile.coord, game)
            offset_direction = get_vector_by_direction(next_path_tile.direction)
            anchor_point = v_add_with_coeff(turn_center_point, offset_direction, 1.0, 0.5 * game.track_tile_size)
            return anchor_point  # WARNING RETURN! ###

        if not self.is_on_turn or dist_to_next_turn == 1:
            next_turn_tile = self.path[next_turn_cp_index]
            turn_center_point = get_tile_center(next_turn_tile.coord, game)
            offset_direction = v_add_with_coeff(get_vector_by_direction(next_turn_tile.direction),
                                                get_vector_by_direction(self.path[self.cur_path_idx].direction),
                                                -1.0, -1.0)
            anchor_point = v_add_with_coeff(turn_center_point, offset_direction,
                                        1.0, 0.25 * game.track_tile_size)

            if car.base.get_distance_to(anchor_point[0], anchor_point[1]) < DISTANCE_BEFORE_TURN:
                # start turning
                offset_direction = v_add_with_coeff(get_vector_by_direction(next_turn_tile.direction),
                                                    get_vector_by_direction(self.path[self.cur_path_idx].direction),
                                                    2.0, -1.0)
                anchor_point = v_add_with_coeff(turn_center_point, offset_direction,
                                                1.0, 0.25 * game.track_tile_size)
                self.is_turning_started = not self.is_on_turn

                if car.base.get_distance_to(anchor_point[0], anchor_point[1]) < game.track_tile_size * 0.3 \
                        and self.is_starts_turn_180_grad(next_path_tile.index):
                    self.is_turn_180_grad = True
        elif self.is_on_turn:
                prev_direction_vector = get_vector_by_direction(self.path[self.cur_path_idx - 1].direction)
                anchor_point = get_tile_center(next_path_tile.coord, game)
                anchor_point = v_add_with_coeff(anchor_point, prev_direction_vector,
                                                1.0, -0.25 * game.track_tile_size)
        else:
            assert(False, 'Unpredicted case in Navigator')

        return anchor_point





    def find_next_turn(self):
        """
        Finds index of the next turn tile, that lies after current tile.
        Returns index and distance (in tiles) to the turn.
        """
        idx = self.cur_path_idx
        dist = 0
        while self.path[self.cur_path_idx].direction == self.path[idx].direction:
            idx += 1
            dist += 1
            if idx >= len(self.path):
                idx = 0
        return idx, dist



    def _get_path_tile(self, idx):
        """
        :type idx: int
        :rtype: PathTile
        """
        self.path
        n = len(self.path)

        if idx < 0:
            print 1
            idx = -(idx + 1)

        while idx >= n:
            idx -= n

        return self.path[idx]

    def is_starts_turn_180_grad(self, idx):
        is_turn = self.path[idx - 1].direction != self.path[idx].direction
        if is_turn:
            next_path_tile = self._get_path_tile(idx + 1)
            next_direction_vector = get_vector_by_direction(next_path_tile.direction)
            prev_direction_vector = get_vector_by_direction(self.path[idx - 1].direction)

            if next_direction_vector[0] == -prev_direction_vector[0] and \
                    next_direction_vector[1] == -prev_direction_vector[1]:
                return True
        return False



