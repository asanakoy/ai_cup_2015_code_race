__author__ = 'artem'

from utils import *
from math_ex import *
from DirectionExt import *
from MyCar import MyCar
from model.World import World
from model.Bonus import Bonus
from pprint import pprint
import PathFinder
from TurnType import TurnType
import numpy as np

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
        self.turn_type = None
        self.anchor_angle = None
        self.ladder_end_point = None
        self.bonus_anchor_point = None

        # index of previous tile (previous tick) in the current path
        # Do not use outside of update() method
        self._prev_path_tile_idx = 0
        self.cur_path_idx = None  # current tile index in the path

        self.is_on_turn = False
        self.is_turning_started = False
        self.is_turn_180_grad = False
        self.PRETURN_DISTANCE = None

    def _get_path(self):
        """
        :rtype: list of PathTile
        """
        if self.is_on_extra_path:
            return self._extra_path
        return self._opt_path

    # Invariant: between two waypoints int he optimal path the chain
    # is always simple (each point occurs only one time).
    # In extra path the chain can contain duplicate points.
    def _find_tile_in_path(self, tile, last_wp_path_index, next_wp_path_index):
        """
        Find index of the til in the path. Search from the last visited waypoint (inclusevly) to the next scheduled waypoint(inclusevely)
        """
        assert type(tile) is tuple
        path = self._get_path()
        assert path is not None

        if last_wp_path_index > next_wp_path_index:
            indices = range(last_wp_path_index, len(path)) + range(0, next_wp_path_index + 1)
        else:
            indices = range(last_wp_path_index, next_wp_path_index + 1)
        for i in indices[::-1]:  # search from the last to the first, because we don't wont to go two times by the same tiles
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

        if not self.is_on_extra_path:
            idx = self._find_tile_in_path(car.cur_tile, self._opt_path_wp_lookup_table[car.base.next_waypoint_index - 1], self._opt_path_wp_lookup_table[car.base.next_waypoint_index])
        else:
            idx = self._find_tile_in_path(car.cur_tile,
                                          self._extra_path_wp_lookup_table[car.base.next_waypoint_index - 1], self._extra_path_wp_lookup_table[car.base.next_waypoint_index])

        # if we strayed from the path
        if idx is None:
            if car.cur_tile == self.path[self._opt_path_wp_lookup_table[car.base.next_waypoint_index - 1]].coord:
                # TODO Maybe remove this??
                # cur tile is the last visited waypoint. The just restsrt optimal path from the last waypoint (current tile)
                idx = self._opt_path_wp_lookup_table[car.base.next_waypoint_index - 1]
            else:
                self._extra_path, self._extra_path_wp_lookup_table \
                    = self.pathfinder.find_extra_path(self._opt_path, car.cur_tile,
                                                      car.base.next_waypoint_index)
                print 'EXTRA_PATH:'
                pprint(self._extra_path)
                self.is_on_extra_path = True
                # from the prev_wp to the new extra tile chain is always simple
                idx = self._find_tile_in_path(car.cur_tile,
                                              self._extra_path_wp_lookup_table[car.base.next_waypoint_index - 1], self._extra_path_wp_lookup_table[car.base.next_waypoint_index])
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


    def get_anchor_point(self, car, world, game):
        """
        :type car: MyCar
        :type world: model.World
        :type game: model.Game
        :rtype: tuple of double
        """
        self.PRETURN_DISTANCE = game.track_tile_size * 1.5
        BONUS_DISTANCE_LOWER = self.PRETURN_DISTANCE + game.track_tile_size * 0.3
        BONUS_DISTANCE_UPPER = self.PRETURN_DISTANCE + game.track_tile_size * 0.7
        self.is_turning_started = False
        self.is_turn_180_grad = False
        self.is_on_long_ladder = False
        self.is_on_turn = self.path[self.cur_path_idx - 1].direction != self.path[self.cur_path_idx].direction
        next_turn_cp_index, dist_to_next_turn = self.find_next_turn()
        next_path_tile = self._get_path_tile(self.cur_path_idx + 1)
        next_next_path_tile = self._get_path_tile(self.cur_path_idx + 2)
        self.anchor_angle = None

        if self.ladder_end_point is not None and car.base.get_distance_to(self.ladder_end_point[0], self.ladder_end_point[1]) < 100.0:
            self.ladder_end_point = None

        self.is_turn_180_grad = self.is_on_turn and self.is_starts_turn_180_grad(self.cur_path_idx)

        if self.is_starts_ladder(self.cur_path_idx - 1):
            self.turn_type = TurnType.LADDER_1

        if self.is_starts_ladder(self.cur_path_idx):
            # going straight through sequential turns
            turn_center_point = get_tile_center(next_path_tile.coord, game)
            offset_direction = get_vector_by_direction(next_path_tile.direction)
            anchor_point = v_add_with_coeff(turn_center_point, offset_direction, 1.0, 0.5 * game.track_tile_size)
            is_ladder_next = self.is_starts_ladder(next_next_path_tile.index)
            if is_ladder_next and self.is_starts_ladder(self.cur_path_idx - 1):
                self.is_on_long_ladder = True
                self.turn_type = TurnType.LADDER_0  # actually it is LADDER_1 too

            if not is_ladder_next:
                self.ladder_end_point = np.array(turn_center_point) + np.array(next_path_tile.direction_vector) * game.track_tile_size * 0.5

        elif not self.is_on_turn or dist_to_next_turn == 1:
            next_turn_tile = self.path[next_turn_cp_index]
            turn_center_point = get_tile_center(next_turn_tile.coord, game)
            offset_direction = v_add_with_coeff(get_vector_by_direction(next_turn_tile.direction),
                                                get_vector_by_direction(self.path[self.cur_path_idx].direction),
                                                -1.0, -1.0)
            anchor_point = v_add_with_coeff(turn_center_point, offset_direction,
                                        1.0, 0.25 * game.track_tile_size)

            if car.base.get_distance_to(anchor_point[0], anchor_point[1]) < self.PRETURN_DISTANCE:
                # start turning
                if dist_to_next_turn == 1:
                    self.anchor_angle = self.get_anchor_angle(car, game, self.path[self.cur_path_idx], next_path_tile)

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
            assert False

        dist_to_anchor = car.base.get_distance_to(anchor_point[0], anchor_point[1])
        min_dist = 10000000
        closest_bonus_anchor = None
        for bonus in world.bonuses:
            dist_anchor_to_bonus = bonus.get_distance_to(anchor_point[0], anchor_point[1])
            if dist_to_anchor > BONUS_DISTANCE_LOWER and dist_anchor_to_bonus > BONUS_DISTANCE_LOWER:
                bonus_anchor, dist_to_bonus = self._get_anchor_for_bonus(bonus, car, game, dist_to_anchor,
                                                                         dist_anchor_to_bonus, BONUS_DISTANCE_LOWER, BONUS_DISTANCE_UPPER)
                if bonus_anchor is not None and dist_to_bonus < min_dist:
                    min_dist = dist_to_bonus
                    closest_bonus_anchor = bonus_anchor

        if closest_bonus_anchor is not None:
            self.bonus_anchor_point = closest_bonus_anchor
            # anchor_point = closest_bonus_anchor
            # self.turn_type = TurnType.BONUS
        else:
            self.bonus_anchor_point = None

        return anchor_point

    def _get_anchor_for_bonus(self, bonus, car, game, dist_to_anchor, dist_anchor_to_bonus, BONUS_DISTANCE_LOWER, BONUS_DISTANCE_UPPER):
        """
        :type bonus: model.Bonus
        :type car: MyCar
        :type game: model.Game
        :return: tuple of double
        """
        dist_to_bonus = car.base.get_distance_to_unit(bonus)
        tile = (int(floor(bonus.x / game.track_tile_size)),  int(floor(bonus.y / game.track_tile_size)))
        cur_tile = self.path[self.cur_path_idx]
        dist_in_tiles = vector_substract(tile, cur_tile.coord)
        orthogonal_direction = (sign(cur_tile.direction_vector[1]), sign(cur_tile.direction_vector[0]))
        is_on_way = sign(dist_in_tiles[0]) == cur_tile.direction_vector[0] and sign(dist_in_tiles[1]) == cur_tile.direction_vector[1]

        prev_tile_was_turn = self.path[self.cur_path_idx - 2].direction != self.path[self.cur_path_idx - 1].direction

        if (not prev_tile_was_turn or car.speed < 12.0) and \
                is_on_way and 300 < dist_to_bonus < dist_to_anchor and \
                ((dist_anchor_to_bonus > BONUS_DISTANCE_UPPER and abs(car.base.get_angle_to_unit(bonus)) < pi / 10.5) or
                 (dist_anchor_to_bonus > BONUS_DISTANCE_LOWER and abs(car.base.get_angle_to_unit(bonus)) < pi / 14.0)):

            bonus_local_coord = [bonus.x - tile[0] * game.track_tile_size, bonus.y - tile[1] * game.track_tile_size]
            offset = max(car.base.width, car.base.height) / 2.0 + game.track_tile_margin + 3

            bonus_coord = [0, 0]
            for i in xrange(2):
                bonus_coord[i] = tile[i] * game.track_tile_size + \
                                 min(max(offset * orthogonal_direction[i], bonus_local_coord[i]),
                                     game.track_tile_size - offset * orthogonal_direction[i])
            print 'BONUS', tile, ' , dist in tiles:', dist_in_tiles
            return bonus_coord , dist_to_bonus

        return None, None

    def find_next_turn(self, _from=None):
        """
        Finds index of the next turn tile, that lies after current tile.
        Returns index and distance (in tiles) to the turn.
        """
        if _from is None:
            _from = self.cur_path_idx
        idx = _from
        dist = 0
        while self.path[_from].direction == self.path[idx].direction:
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
        n = len(self.path)

        if idx < 0:
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

    def is_starts_ladder(self, idx):
        tile = self._get_path_tile(idx)
        idx = tile.index
        is_turn_180_grad = self.is_starts_turn_180_grad(idx)
        next_turn_idx, dist_to_next_turn = self.find_next_turn(idx)

        if not is_turn_180_grad and dist_to_next_turn == 1:
            next_path_tile = self.path[next_turn_idx]
            next_next_path_tile = self._get_path_tile(idx + 2)

            if next_path_tile.direction != next_next_path_tile.direction and \
                    tile.direction == next_next_path_tile.direction and \
                    not self.is_starts_turn_180_grad(next_next_path_tile.index):
                return True
        return False


    def get_anchor_angle(self, me, game, path_tile, next_path_tile):
        dir = np.array(path_tile.direction_vector)
        next_dir = np.array(next_path_tile.direction_vector)

        offset = (next_dir - dir) * 0.5 * game.track_tile_size
        next_tle_center = np.array(get_tile_center(next_path_tile.coord, game))
        K = next_tle_center + offset
        D = next_tle_center - offset
        h = min(me.base.height, me.base.width) / 2.0 + game.track_tile_margin + 25
        c = me.base.get_distance_to(K[0], K[1])
        if c < h:
            c = h + 30.0
        betta = pi / 2.0 - acos(h / c)

        O = np.array([me.base.x, me.base.y])
        betta_sign = sign(np.cross(K - O, D - O))

        anchor_angle = me.base.get_angle_to(K[0], K[1]) + betta_sign * betta
        return anchor_angle


