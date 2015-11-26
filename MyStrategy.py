from model.Car import Car
from model.Game import Game
from model.Move import Move
from model.World import World
from model.TileType import TileType
from model.OilSlick import OilSlick
from math import *
import numpy as np
from pprint import pprint
from random import random
from  DirectionExt import *
from MyCar import MyCar
from Navigator import Navigator
from physics import Physics
from CarState import CarState
from utils import *
from math_ex import *
import Shooter

class MyStrategy:
    SPEED_HEAP_SIZE = 20
    GO_BACK_CD = 100
    DEBUG_LR = False

    def __init__(self):
        self.tmp = None
        self.navigator = None
        self.physics = None
        self.mycar = None
        self.go_back_cd = MyStrategy.GO_BACK_CD  # need to get positive speed at least 0.75
        self.go_back = 0
        self.driving_direction_vector = None
        self.debug = None
        self.speed_limit_before_turn = None
        if MyStrategy.DEBUG_LR:
            try:
                from debug.debug_client import DebugClient
                from debug.debug_client import Color
            except ImportError:
                pass
            else:
                self.debug = DebugClient()
                self.green = Color(r=0.0, g=1.0, b=0.0)


    def preproc(self, world, game):
        print 'world %d x %d' % (world.width, world.height)
        pprint(map(list, zip(*world.tiles_x_y)))
        print world.waypoints
        print '====================='
        self.navigator = Navigator(world)
        self.physics = Physics(world, game)

    def update(self, me, world, game):
        if world.tick == 0:
            self.preproc(world, game)

        self.mycar = MyCar(me, game.track_tile_size)
        self.navigator.update_state(self.mycar)

        if world.tick == 0:
            pprint(self.navigator.path)
            print "car.width %d, car.height: %d" % (me.width, me.height)

        print 'Tick[%d] TILE%s P(%.16f, %.16f)' % (world.tick, str(self.mycar.cur_tile), self.mycar.base.x, self.mycar.base.y)
        # print 'Nitro:', me.nitro_charge_count

        self.driving_direction_vector = tuple(get_vector_by_direction(
                                            self.navigator.path[self.navigator.cur_path_idx].direction))

        self.speed_limit_before_turn = 23
        if self.navigator.ladder_end_point is not None:
            self.speed_limit_before_turn = 21
        if self.navigator.is_turn_180_grad:
            self.speed_limit_before_turn = 21  # Doesn't make sens. TODO calculate and store in navigator next turn Type


    def move(self, me, world, game, move):
        """
        @type me: Car
        @type world: World
        @type game: Game
        @type move: Move
        """
        ##################
        if len(world.players) == 2:
            print '2x2 Game. Do nothing.'
            return
        if me.finished_track:
            return
        self.update(me, world, game)
        anchor_point = self.navigator.get_anchor_point(self.mycar, world, game)
        is_turning_started = self.navigator.is_turning_started
        ##################

        next_turn_idx, dist_to_next_turn = self.navigator.find_next_turn()

        if self.navigator.anchor_angle is not None and self.mycar.speed > 10.0:
            angle_to_anchor_point = self.navigator.anchor_angle
        else:
            angle_to_anchor_point = me.get_angle_to(anchor_point[0], anchor_point[1])

        if self.navigator.bonus_anchor_point is not None:
            angle_to_anchor_point = me.get_angle_to(self.navigator.bonus_anchor_point[0], self.navigator.bonus_anchor_point[1])


        distance_to_anchor_point = me.get_distance_to(anchor_point[0], anchor_point[1])
        if self.tmp != me.next_waypoint_index:
            self.tmp = me.next_waypoint_index
            print "NEW_WP:", (me.next_waypoint_x, me.next_waypoint_y)

        print 'V(%.16f, %.16f) V_HYP(%.16f)' % (me.speed_x, me.speed_y, self.mycar.speed)
        print 'ANG(%.16f) ANG_V(%.16f)' % (me.angle, self.mycar.base.angular_speed)
        print 'EP(%.16f) WT(%.16f)' % (me.engine_power, me.wheel_turn)
        print 'ANCH_ANG(%.5f) ANCH_DIST(%.5f)' % (angle_to_anchor_point, distance_to_anchor_point)
        print 'PRJCT(%d)' % (me.projectile_count)
        print 'next Anchor:', anchor_point
        print 'is_on_long_ladder:', self.navigator.is_on_long_ladder
        if self.debug:
            self.debug.use_tile_coords(False)
            with self.debug.post() as dbg:
                dbg.circle(anchor_point[0],
                           anchor_point[1],
                           25.0, self.green)
                dbg.text(me.x, me.y, '%.2f' % self.mycar.speed, (0.0, 0.0, 0.0))

                next_wp_tile = world.waypoints[me.next_waypoint_index]
                next_wp_pos = ((next_wp_tile[0] + 0.5) * game.track_tile_size, (next_wp_tile[1] + 0.5) * game.track_tile_size)
                dbg.fill_circle(next_wp_pos[0], next_wp_pos[1], 30, (1.0, 0.0, 0.0))
                if self.navigator.anchor_angle is not None:
                    vec = np.array([sin(me.angle - angle_to_anchor_point), cos(me.angle - angle_to_anchor_point)])
                    point = np.array([me.x, me.y]) + vec * 200.0
                    dbg.line(me.x, me.y, point[0], point[1], (1.0, 0.0, 0.0))

        if self.go_back:
            self.go_back -= 1
            move.wheel_turn = 0
            move.engine_power = -1.0
            if self.go_back > 10:
                move.wheel_turn = -sign(angle_to_anchor_point)
            return
        else:
            self.go_back_cd = max(0, self.go_back_cd - 1)

        if ((self.navigator.is_turning_started or self.navigator.is_turn_180_grad) and \
                world.tick <= game.initial_freeze_duration_ticks + 50) or \
                (self.mycar.speed >= 0 and world.tick > game.initial_freeze_duration_ticks + 50):
            if self.navigator.is_turn_180_grad:
                move.wheel_turn = sign(angle_to_anchor_point)
            else:
                move.wheel_turn = (angle_to_anchor_point * 32.0 / pi)

        move.engine_power = 1.0

        move.use_nitro = self.should_use_nitro(me, world, game, distance_to_anchor_point, angle_to_anchor_point)

        if not self.go_back_cd and world.tick > game.initial_freeze_duration_ticks + 100 and abs(self.mycar.speed) < 0.12:
            self.go_back = 90
            self.go_back_cd = MyStrategy.GO_BACK_CD
            print 'Start go BACK'

        if not is_turning_started and abs(angle_to_anchor_point) > pi*3.0/18.0 and abs(self.mycar.speed) * abs(angle_to_anchor_point) > 12 * pi/4:
            move.brake = True

        # ((1.6 + (self.mycar.speed - speed_limit_before_turn) / 10) * game.track_tile_size) \
        car_state = CarState.from_car(me)
        car_state.engine_power_lim = move.engine_power
        car_state.brake = False

        #  TODO find out when ladder ends to start braking
        if not is_turning_started and (not self.navigator.is_on_turn or self.navigator.ladder_end_point is not None) and \
                        self.mycar.speed > self.speed_limit_before_turn:
            tmp1, braking_dist, tmp2 = self.physics.calc_brake_distance(car_state, self.speed_limit_before_turn)
            print 'braking_dst(%.5f)' % braking_dist
            if self.navigator.ladder_end_point is not None:
                dist = me.get_distance_to(self.navigator.ladder_end_point[0], self.navigator.ladder_end_point[1])
                move.brake = 100 < dist <= game.track_tile_size + braking_dist
            elif self.navigator.PRETURN_DISTANCE < distance_to_anchor_point <= self.navigator.PRETURN_DISTANCE + braking_dist:
                move.brake = True


        move.throw_projectile = Shooter.should_shoot(self.mycar, world, game)
        if move.throw_projectile:
            print 'SHOOT--->'
        move.spill_oil = self.should_spill_oil(me, world, game)

        print move_to_str(move)

########################################################################################################################

    def should_spill_oil(self, me, world, game):
        if me.oil_canister_count == 0 or self.mycar.speed < 2.0:
            return False

        OIL_SLICK_RADIUS = 150
        if self.navigator.is_turning_started and world.tick > game.initial_freeze_duration_ticks + 385:
            lower_dist = max(me.width, me.height) + 10 + OIL_SLICK_RADIUS / 5.0
            for car in world.cars:
                if not car.teammate and lower_dist < me.get_distance_to_unit(car) < game.track_tile_size * 8.0 \
                        and abs(me.get_angle_to_unit(car)) > pi / 2:
                    print 'SPILL_OIL: anlg_to_car({}), dist({})'.format(me.get_angle_to_unit(car),\
                            me.get_distance_to_unit(car))
                    return True
        return False

    def get_increased_cp_idx(self, cp_index):
        return cp_index + 1 if cp_index + 1 < len(self.check_points) else 0


    def should_use_nitro(self, me, world, game, distance_to_anchor_point, angle_to_anchor_point):
        if me.nitro_charge_count == 0 or me.remaining_nitro_cooldown_ticks > 0:
            return False
        # if dist_to_next_turn is not None and world.tick > game.initial_freeze_duration_ticks and dist_to_next_turn > 2:
        #     return True

        if (not self.navigator.is_on_turn or self.navigator.is_on_long_ladder) and not self.navigator.is_turning_started \
                and me.angular_speed < 0.5 and world.tick > game.initial_freeze_duration_ticks:
            # TODO check that we haven't recently strayed from the path

            car_state = CarState.from_car(me)
            car_state.engine_power = game.nitro_engine_power_factor
            car_state.engine_power_lim = game.nitro_engine_power_factor
            car_state.brake = False
            dist_on_nitro, end_nitro_state = self.physics.simulate(car_state, game.nitro_duration_ticks)
            # TODO find accurate solution
            ticks_to_bake, braking_dist, tmp2 = self.physics.calc_brake_distance(car_state, self.speed_limit_before_turn)

            is_pretty_far_from_turn = dist_on_nitro * 0.95 <= (distance_to_anchor_point - self.navigator.PRETURN_DISTANCE)

            if self.navigator.is_on_long_ladder:
                angle_delta = abs(angle_to_anchor_point)
                angle_threshold = pi / 72.0
            else:
                angle_delta = abs(acos(sum(map(lambda a, b: a*b, self.driving_direction_vector,
                                                                 self.mycar.direction_vector))))
                angle_threshold = pi / 18.0

            if (is_pretty_far_from_turn or self.navigator.is_on_long_ladder) \
                    and angle_delta < angle_threshold and me.remaining_oiled_ticks == 0:
                return True
        return False

# def get_main_direction(car):
#     PAD = pi/18
#     A = -(pi/4 - PAD)
#     B = (pi/4 - PAD)
#
#     if A <= car.angle <= B:
#         return (1, 0)
#
#     if A - pi/2 <= car.angle <= B - pi/2:
#         return (0, -1)
#
#     if A + pi/2 <= car.angle <= B + pi/2:
#         return (0, 1)
#
#     if car.angle <= B - pi or car.angle >= A + pi:
#         return (-1, 0)
#
#     return (0, 0)

