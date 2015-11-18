from model.Car import Car
from model.Game import Game
from model.Move import Move
from model.World import World
from model.TileType import TileType
from math import *
from pprint import pprint
from random import random
import PathFinder
from PathFinder import sign

class MyStrategy:
    SPEED_HEAP_SIZE = 20
    GO_BACK_CD = 100

    def __init__(self):
        self.cur_tile = (-1, -1)
        self.prev_waypoint = (-1, -1)
        self.go_back_cd = MyStrategy.GO_BACK_CD # need to get positive speed at least 0.75
        self.go_back = 0
        self.check_points = []
        self.check_points_directions = []
        self.cur_cp_index = None
        self.next_cp_index = 0
        self.prev_path_tile = None
        self.turn_started_time = -100000

    def preproc(self, world):
        if len(world.players) == 2:
            print 'WARNING 2x2 game!'
            self.check_points = world.waypoints
            self.check_points_directions = [world.height * [0] for _ in xrange(world.width)]  # JUST DUMMY
        else:
            (self.check_points, self.check_points_directions) = \
                PathFinder.find_check_points(world.tiles_x_y, world.waypoints, world.width, world.height)

    def update(self, me, world, game):
        if world.tick == 0:
            print 'world %d x %d' % (world.width, world.height)
            pprint(map(list, zip(*world.tiles_x_y)))
            print world.waypoints
            print '====================='
            self.preproc(world)
            pprint(self.check_points)
            pprint(self.check_points_directions)

        self.cur_tile = (floor(me.x / game.track_tile_size),  floor(me.y / game.track_tile_size))
        print 'Tick %d %d, %d' % (world.tick, self.cur_tile[0], self.cur_tile[1])
        # print 'Nitro:', me.nitro_charge_count
        print 'Angular speed:', me.angular_speed

        if self.cur_tile == self.check_points[self.next_cp_index]:
            self.cur_cp_index = self.next_cp_index
            self.next_cp_index += 1
            if self.next_cp_index >= len(self.check_points):
                self.next_cp_index = 0
            print 'Cp passed!'
            print 'NEXT CP INDEX:', self.next_cp_index
        elif self.cur_cp_index is not None and self.cur_tile != self.check_points[self.cur_cp_index]:
            self.cur_cp_index = None


        self.driving_direction = self.get_current_driving_direction()
        self.driving_direction_vector = tuple(PathFinder.get_vector_by_direction(self.driving_direction))

        if self.driving_direction != PathFinder.UNKNOWN_DIRECTION:
            self.prev_path_tile = self.cur_tile



    def get_next_anchor_point(self, me, world, game):
        is_turning_started = False
        if self.driving_direction == PathFinder.UNKNOWN_DIRECTION:
            anchor_point = PathFinder.get_tile_center(self.prev_path_tile, game)
            return anchor_point, is_turning_started

        next_turn_cp_index = self.get_next_turn_cp_index()
        tile_offset = 0.25 * game.track_tile_size

        next_path_tile = tuple(map(lambda a, b: a + b, self.cur_tile, self.driving_direction_vector))

        if not self.is_on_turn() or next_path_tile == self.check_points_directions[next_turn_cp_index]:
            turn_center_point = PathFinder.get_tile_center(self.check_points[next_turn_cp_index], game)
            anchor_point = [0, 0]
            offset_direction = map(lambda a, b: -a - b,
                        PathFinder.get_vector_by_direction(self.check_points_directions[next_turn_cp_index]),
                        self.driving_direction_vector)
            for i in range(2):
                anchor_point[i] = turn_center_point[i] + offset_direction[i] * 0.28 * game.track_tile_size

            if me.get_distance_to(anchor_point[0], anchor_point[1]) < game.track_tile_size * 1.5:
                offset_direction = map(lambda a, b: a - b,
                                       PathFinder.get_vector_by_direction(self.check_points_directions[next_turn_cp_index]),
                                       self.driving_direction_vector)
                for i in range(2):
                    anchor_point[i] = turn_center_point[i] + offset_direction[i] * tile_offset
                is_turning_started = True
                self.turn_started_time = world.tick

        else:
            prev_direction = self.check_points_directions[self.cur_cp_index - 1]
            prev_direction_vector = PathFinder.get_vector_by_direction(prev_direction)
            anchor_point = PathFinder.get_tile_center(next_path_tile, game)
            for i in xrange(2):
                anchor_point[i] -= prev_direction_vector[i] * 0.25 * game.track_tile_size

        return anchor_point, is_turning_started



    def move(self, me, world, game, move):
        """
        @type me: Car
        @type world: World
        @type game: Game
        @type move: Move
        """
        ##################
        self.update(me, world, game)
        anchor_point, is_turning_started = self.get_next_anchor_point(me, world, game)
        ##################

        is_on_turn = self.is_on_turn()
        dist_to_next_turn = self.get_distance_to_next_turn()

        angle_to_anchor_point = me.get_angle_to(anchor_point[0], anchor_point[1])
        speed_module = hypot(me.speed_x, me.speed_y)
        car_direction_vector = get_direction_vector(me)

        speed_sign = sign(car_direction_vector[0] * me.speed_x + car_direction_vector[1] * me.speed_y)
        speed = speed_sign * speed_module
        print 'speed', speed
        print 'me.wheel_turn:', me.wheel_turn
        print 'me.engine_power:', me.engine_power
        if self.go_back:
            self.go_back -= 1
            move.wheel_turn = 0
            move.engine_power = -1.0
            if self.driving_direction != PathFinder.UNKNOWN_DIRECTION and self.go_back > 10:
                move.wheel_turn = -sign(angle_to_anchor_point)
            return
        else:
            self.go_back_cd = max(0, self.go_back_cd - 1)

        if speed_sign >= 0 and world.tick > game.initial_freeze_duration_ticks + 50:
            move.wheel_turn = (angle_to_anchor_point * 32.0 / pi)

        move.engine_power = 1.0

        if world.tick > game.initial_freeze_duration_ticks and dist_to_next_turn > 2:
                move.use_nitro = True
        elif self.driving_direction != PathFinder.UNKNOWN_DIRECTION and not is_on_turn \
                and me.angular_speed < 2.0:

            angle_delta = acos(sum(map(lambda a, b: a*b, self.driving_direction_vector,
                                                         car_direction_vector)))
            if world.tick > game.initial_freeze_duration_ticks and dist_to_next_turn > 3 \
                    and angle_delta < pi / 12.0:
                move.use_nitro = True

        if not self.go_back_cd and world.tick > game.initial_freeze_duration_ticks + 100 and speed_module < 0.12:
            self.go_back = 90
            self.go_back_cd = MyStrategy.GO_BACK_CD
            print 'Start go BACK'

        if abs(angle_to_anchor_point) > pi*4.0/18.0 and speed_module * abs(angle_to_anchor_point) > 15 * pi/4:
            move.brake = True

        next_turn_tile = map(lambda a, b: a + dist_to_next_turn * b, self.cur_tile, driving_direction_vector)
        next_turn_point = [(next_turn_tile[0] + 0.5) * game.track_tile_size,
                           (next_turn_tile[1] + 0.5) * game.track_tile_size]

        breaking_distance = me.get_distance_to(next_turn_point[0], next_turn_point[1])

        main_direction = get_main_direction(me)
        if main_direction != (0, 0) and breaking_distance < 2 * game.track_tile_size:
            if speed >= 30.0:
                move.brake = True
            # elif breaking_distance < 1.5 * game.track_tile_size and speed >= 20:
            #     move.brake = True

        if main_direction != (0, 0) and (driving_direction != PathFinder.UNKNOWN_DIRECTION and dist_to_next_turn <= 1) \
                and speed > 15.0:
            move.brake = True

        move.throw_projectile = should_shoot(me, world, game)
        move.spill_oil = self.should_spill_oil(me, world, game, is_on_turn)

########################################################################################################################

    def should_spill_oil(self, me, world, game, is_on_turn):
        if is_on_turn and world.tick > game.initial_freeze_duration_ticks + 200:
            for car in world.cars:
                if not car.teammate and me.get_distance_to_unit(car) < game.track_tile_size * 1.5:
                    return True
        return False

    def is_turn(self, cp_index):
        return self.check_points_directions[cp_index] != self.check_points_directions[cp_index - 1]

    def is_on_turn(self):
        if self.cur_tile in self.check_points:
            prev_cp_index = self.next_cp_index - 2  # it was already incremented, because we are on CP now
        else:
            prev_cp_index = self.next_cp_index - 1
        return self.get_current_driving_direction() != self.check_points_directions[prev_cp_index]

    def get_distance_to_next_turn(self):
        ind = self.get_next_turn_cp_index()
        if ind is None:
            return None

        diff = map(lambda a, b: abs(a-b), self.cur_tile, self.check_points[ind])
        distance = diff[0] + diff[1]
        assert(diff[0] * diff[1] == 0)
        return distance

    ## Does not count current tile as turn
    def get_next_turn_cp_index(self):
        ind = self.next_cp_index
        cur_driving_direction = get_driving_direction(self.cur_tile, self.check_points[self.next_cp_index])
        if cur_driving_direction == PathFinder.UNKNOWN_DIRECTION:
            assert False
            return None

        while self.check_points_directions[ind] == cur_driving_direction:
            ind += 1
            if ind >= len(self.check_points):
                ind = 0
        return ind

    def get_current_driving_direction(self):
        return get_driving_direction(self.cur_tile, self.check_points[self.next_cp_index])


def should_shoot(me, world, game):
    for car in world.cars:
        if not car.teammate and car.durability > 0 and abs(me.get_angle_to_unit(car)) < pi / 18 and \
                me.get_distance_to_unit(car) < game.track_tile_size:
            return True

    return False


def get_direction_vector(car):
    return (cos(car.angle), sin(car.angle))


# if it is not a straight direction returns UNKNOWN_DIRECTION
def get_driving_direction(cur_tile, next_cp):
    vector = map(lambda x, y: sign(x - y), next_cp, cur_tile)
    direction = PathFinder.get_direction_by_vector(vector)
    return direction


def get_main_direction(car):
    PAD = pi/18
    A = -(pi/4 - PAD)
    B = (pi/4 - PAD)

    if A <= car.angle <= B:
        return (1, 0)

    if A - pi/2 <= car.angle <= B - pi/2:
        return (0, -1)

    if A + pi/2 <= car.angle <= B + pi/2:
        return (0, 1)

    if car.angle <= B - pi or car.angle >= A + pi:
        return (-1, 0)

    return (0, 0)


def have_obstacles(cur_tile, direction, world, dist):
    obstacles = {(1,0): [TileType.RIGHT_TOP_CORNER, TileType.RIGHT_BOTTOM_CORNER, TileType.LEFT_HEADED_T],
                (-1,0): [TileType.LEFT_TOP_CORNER, TileType.LEFT_BOTTOM_CORNER, TileType.RIGHT_HEADED_T],
                 (0,1): [TileType.LEFT_BOTTOM_CORNER, TileType.RIGHT_BOTTOM_CORNER, TileType.TOP_HEADED_T],
                (0,-1): [TileType.LEFT_TOP_CORNER, TileType.RIGHT_TOP_CORNER, TileType.BOTTOM_HEADED_T]}

    max_point = (world.width - 1, world.height - 1)

    next = (dist + 1) * [cur_tile]
    for i in xrange(1, dist + 1):
        next[i] = map(lambda x, y: x + y, next[i-1], direction)

    for i in xrange(dist + 1):
        if tuple(next[i]) < (0, 0) or tuple(next[i]) > max_point:
            return True
        if world.tiles_x_y[int(next[i][0])][int(next[i][1])] in obstacles[direction]:
            return True

    return False



def tileTypeToStr(t):
    if t == TileType.LEFT_TOP_CORNER:
        return "LEFT_TOP_CORNER"
    if t == TileType.RIGHT_TOP_CORNER:
        return "RIGHT_TOP_CORNER"
    if t == TileType.LEFT_BOTTOM_CORNER:
        return "LEFT_BOTTOM_CORNER"
    if t == TileType.RIGHT_BOTTOM_CORNER:
        return "RIGHT_BOTTOM_CORNER"


