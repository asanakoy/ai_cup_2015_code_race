from model.Car import Car
from model.Game import Game
from model.Move import Move
from model.World import World
from model.TileType import TileType
from model.OilSlick import OilSlick
from math import *
from pprint import pprint
from random import random
from  DirectionExt import *
from MyCar import MyCar
from Navigator import Navigator
from utils import *
import Shooter

class MyStrategy:
    SPEED_HEAP_SIZE = 20
    GO_BACK_CD = 100
    DEBUG_LR = False

    def __init__(self):
        self.tmp = None
        self.navigator = None
        self.mycar = None
        self.go_back_cd = MyStrategy.GO_BACK_CD  # need to get positive speed at least 0.75
        self.go_back = 0
        self.driving_direction_vector = None
        self.debug = None
        if MyStrategy.DEBUG_LR:
            try:
                from debug.debug_client import DebugClient
                from debug.debug_client import Color
            except ImportError:
                pass
            else:
                self.debug = DebugClient()
                self.green = Color(r=0.0, g=1.0, b=0.0)


    def preproc(self, world):
        print 'world %d x %d' % (world.width, world.height)
        pprint(map(list, zip(*world.tiles_x_y)))
        print world.waypoints
        print '====================='
        self.navigator = Navigator(world)

    def update(self, me, world, game):
        if world.tick == 0:
            self.preproc(world)

        self.mycar = MyCar(me, game.track_tile_size)
        self.navigator.update_state(self.mycar)

        if world.tick == 0:
            pprint(self.navigator.path)
            print "car.width %d, car.height: %d" % (me.width, me.height)

        print 'Tick[%d] %s {%.2f, %.2f}' % (world.tick, str(self.mycar.cur_tile), self.mycar.base.x, self.mycar.base.y)
        # print 'Nitro:', me.nitro_charge_count

        self.driving_direction_vector = tuple(get_vector_by_direction(
                                            self.navigator.path[self.navigator.cur_path_idx].direction))


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

        angle_to_anchor_point = me.get_angle_to(anchor_point[0], anchor_point[1])
        if self.tmp != me.next_waypoint_index:
            self.tmp = me.next_waypoint_index
            print "NEW_WP:", (me.next_waypoint_x, me.next_waypoint_y)
        print 'SP(%.5f) EP(%.5f) ANSP(%.5f)' % (self.mycar.speed, me.engine_power, self.mycar.base.angular_speed)
        print 'WT(%.5f) ANGL(%.5f) ANCH_ANG(%.5f)' % (me.wheel_turn, me.angle, angle_to_anchor_point)
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

        if self.go_back:
            self.go_back -= 1
            move.wheel_turn = 0
            move.engine_power = -1.0
            if self.go_back > 10:
                move.wheel_turn = -sign(angle_to_anchor_point)
            return
        else:
            self.go_back_cd = max(0, self.go_back_cd - 1)

        if self.mycar.speed >= 0 and world.tick > game.initial_freeze_duration_ticks + 50:
            if self.navigator.is_turn_180_grad:
                move.wheel_turn = sign(angle_to_anchor_point)
            else:
                move.wheel_turn = (angle_to_anchor_point * 32.0 / pi)

        move.engine_power = 1.0

        if dist_to_next_turn is not None and world.tick > game.initial_freeze_duration_ticks and dist_to_next_turn > 2:
                move.use_nitro = True
        elif (not self.navigator.is_on_turn or self.navigator.is_on_long_ladder) and me.angular_speed < 0.5 and world.tick > game.initial_freeze_duration_ticks:
            # TODO check that we haven't recently strayed from the path

            if self.navigator.is_on_long_ladder:
                angle_delta = abs(angle_to_anchor_point)
                angle_threshold = pi / 72.0
            else:
                angle_delta = abs(acos(sum(map(lambda a, b: a*b, self.driving_direction_vector,
                                                             self.mycar.direction_vector))))
                angle_threshold = pi / 18.0

            if world.tick > game.initial_freeze_duration_ticks and \
                    (dist_to_next_turn > 3 or self.navigator.is_on_long_ladder) \
                    and angle_delta < angle_threshold:
                move.use_nitro = True

        if not self.go_back_cd and world.tick > game.initial_freeze_duration_ticks + 100 and abs(self.mycar.speed) < 0.12:
            self.go_back = 90
            self.go_back_cd = MyStrategy.GO_BACK_CD
            print 'Start go BACK'

        if not is_turning_started and abs(angle_to_anchor_point) > pi*4.0/18.0 and abs(self.mycar.speed) * abs(angle_to_anchor_point) > 12 * pi/4:
            move.brake = True

        speed_limit_before_turn = 23
        if self.navigator.is_turn_180_grad:
            speed_limit_before_turn = 21

        if not is_turning_started and 1.5 * game.track_tile_size < \
                 me.get_distance_to(anchor_point[0], anchor_point[1]) \
                 < ((1.6 + (self.mycar.speed - speed_limit_before_turn) / 10) * game.track_tile_size) \
                 and self.mycar.speed > speed_limit_before_turn:
              move.brake = True

        move.throw_projectile = Shooter.should_shoot(self.mycar, world, game)
        if move.throw_projectile:
            print 'SHOOT--->'
        move.spill_oil = self.should_spill_oil(me, world, game)

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

