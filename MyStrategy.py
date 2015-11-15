from model.Car import Car
from model.Game import Game
from model.Move import Move
from model.World import World
from model.TileType import TileType
from math import *
from pprint import pprint
from random import random
# import numpy as np

class MyStrategy:
    SPEED_HEAP_SIZE = 20
    GO_BACK_CD = 100
    def __init__(self):
        self.prev_waypoint = (-1, -1)
        self.go_back_cd = MyStrategy.GO_BACK_CD # need to get positive speed at least 0.75
        self.go_back = 0

    def move(self, me, world, game, move):
        """
        @type me: Car
        @type world: World
        @type game: Game
        @type move: Move
        """
        ##################
        if world.tick == 0:
            print 'world %d x %d' % (world.width, world.height)
            pprint(map(list, zip(*world.tiles_x_y)))
            print world.waypoints

        cur_tile = (floor(me.x / game.track_tile_size),  floor(me.y / game.track_tile_size))
        print 'Tick %d %d, %d' % (world.tick, cur_tile[0], cur_tile[1])
        # print 'Nitro:', me.nitro_charge_count
        print 'Angular speed:', me.angular_speed
        next_wp_type = world.tiles_x_y[me.next_waypoint_x][me.next_waypoint_y]
        if self.prev_waypoint != (me.next_waypoint_x, me.next_waypoint_y):
            print 'wp: %s(%d) %d %d' % (tileTypeToStr(next_wp_type), next_wp_type, me.next_waypoint_x, me.next_waypoint_y)
            self.prev_waypoint = (me.next_waypoint_x, me.next_waypoint_y)

        ##################

        next_wp_X = (me.next_waypoint_x + 0.5) * game.track_tile_size
        next_wp_Y = (me.next_waypoint_y + 0.5) * game.track_tile_size

        cornerTileOffset = 0.25 * game.track_tile_size


        if next_wp_type == TileType.LEFT_TOP_CORNER:
                next_wp_X += cornerTileOffset
                next_wp_Y += cornerTileOffset

        elif next_wp_type == TileType.RIGHT_TOP_CORNER:
                next_wp_X -= cornerTileOffset
                next_wp_Y += cornerTileOffset

        elif next_wp_type == TileType.LEFT_BOTTOM_CORNER:
                next_wp_X += cornerTileOffset
                next_wp_Y -= cornerTileOffset

        elif next_wp_type == TileType.RIGHT_BOTTOM_CORNER:
                next_wp_X -= cornerTileOffset
                next_wp_Y -= cornerTileOffset


        angleToWaypoint = me.get_angle_to(next_wp_X, next_wp_Y)
        speedModule = hypot(me.speed_x, me.speed_y)
        car_direction_vector = get_direction_vector(me)
        speed_sign = sign(car_direction_vector[0] * me.speed_x + car_direction_vector[1] * me.speed_y)
        speed = speed_sign * speedModule
        print 'speed', speed
        print 'me.wheel_turn:', me.wheel_turn
        print 'me.engine_power:', me.engine_power
        if self.go_back:
            self.go_back -= 1
            move.wheel_turn = 0
            move.engine_power = -1.0
            return
        else:
            self.go_back_cd = max(0, self.go_back_cd - 1)

        if speed_sign >= 0:
            move.wheel_turn = (angleToWaypoint * 32.0 / pi)
            if abs(angleToWaypoint) > pi/4 or \
                    (world.tick > game.initial_freeze_duration_ticks + 100 and abs(angleToWaypoint) > pi/8.0 and
                     speedModule < 0.1):
                move.wheel_turn = sign(angleToWaypoint)

        move.engine_power = 1.0

        main_direction = get_main_direction(me)
        if main_direction != (0, 0) and me.angular_speed < 5.0:
            diff_with_next_cp_x = me.next_waypoint_x - cur_tile[0]
            diff_with_next_cp_y = me.next_waypoint_y - cur_tile[1]
            if (main_direction[0] == sign(diff_with_next_cp_x) and
                    main_direction[1] == sign(diff_with_next_cp_y) and
                    not have_obstacles(cur_tile, main_direction, world, 2)):
                move.engine_power = 1.0
                if world.tick > game.initial_freeze_duration_ticks:
                    move.use_nitro = True
            else:
                if world.tick > game.initial_freeze_duration_ticks + 200:
                    move.spill_oil = True

        if not self.go_back_cd and world.tick > game.initial_freeze_duration_ticks + 100 and speedModule < 0.1:
            self.go_back = 90
            self.go_back_cd = MyStrategy.GO_BACK_CD
            print 'Start go BACK'

        if abs(angleToWaypoint) > pi*4.0/18.0 and speedModule * abs(angleToWaypoint) > 15 * pi/4:
            move.brake = True

        if main_direction != (0, 0) and speed > 15.0 and have_obstacles(cur_tile, main_direction, world, 1):
            move.brake = True

        move.throw_projectile = should_shoot(me, world, game)


def should_shoot(me, world, game):
    for car in world.cars:
        if not car.teammate and abs(me.get_angle_to_unit(car)) < pi / 18 and \
                me.get_distance_to_unit(car) < game.track_tile_size:
            return True

    return False


def get_direction_vector(car):
    return (cos(car.angle), sin(car.angle))


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


def sign(a):
    return (a > 0) - (a < 0)


