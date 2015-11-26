__author__ = 'artem'

# from model.Car import Car
from model.CarType import CarType
# from model.Game import Game
# from model.Move import Move
# from model.World import World
# from model.TileType import TileType
from math import *
from math_ex import *
from pprint import pprint
# from random import random
import numpy as np
from scipy.spatial import distance
from CarState import CarState
import copy


def sign(a):
    return (a > 0) - (a < 0)


def limit(val, lim):
    return max(-lim, min(lim, val))



def calc_path_rude(v_0, car_power_0, limit_car_power, t):
    car_engine_power_change_per_tick = 0.025 #game.car_engine_power_change_per_tick
    buggy_engine_forward_power = 0.25 #game.buggy_engine_forward_power
    buggy_engine_rear_power = -0.1875 #game.buggy_engine_rear_power

    speed = v_0
    cur_power = car_power_0
    path_length = 0
    power_change_direction = sign(limit_car_power - car_power_0)
    print power_change_direction

    for i in range(1, t+1):
        cur_power += car_engine_power_change_per_tick * power_change_direction
        if power_change_direction > 0:
            cur_power = min(limit_car_power, cur_power)
        else:
            cur_power = max(limit_car_power, cur_power)
        a = cur_power * (buggy_engine_forward_power if cur_power > 0 else -buggy_engine_rear_power)
        speed += a
        path_length += speed

    return path_length, speed, cur_power


class Physics:

    PHYS_ITER = 10
    PHYS_DT = 0.1

    def __init__(self, world, game):
        self.carAccel = np.array([0.0, 0.0])
        self.carAccel[CarType.BUGGY] = game.buggy_engine_forward_power / game.buggy_mass * Physics.PHYS_DT
        self.carAccel[CarType.JEEP] = game.jeep_engine_forward_power / game.jeep_mass * Physics.PHYS_DT
        self.frictMul = pow(1 - game.car_movement_air_friction_factor, Physics.PHYS_DT)
        self.longFrict = game.car_lengthwise_movement_friction_factor * Physics.PHYS_DT
        self.crossFrict = game.car_crosswise_movement_friction_factor * Physics.PHYS_DT
        self.carRotFactor = game.car_angular_speed_factor
        self.rotFrictMul = pow(1 - game.car_rotation_air_friction_factor, Physics.PHYS_DT)
        self.angFrict = game.car_rotation_friction_factor * Physics.PHYS_DT

        self.world = world
        self.game = game

    def simulate(self, car_state_, ticks_count):
        car_state = copy.deepcopy(car_state_)
        start_pos = copy.deepcopy(car_state.pos)
        while ticks_count:
            self.calc(car_state)
            ticks_count -= 1
        dist = distance.euclidean(start_pos, car_state.pos)
        return dist, car_state


    def calc(self, car_state):
        """
        Cahanges the argument car_state
        @type car_state: CarState
        """
        angle = car_state.angle
        dir = np.array([cos(angle), sin(angle)])
        spd = car_state.speed
        pos = car_state.pos
        if car_state.brake:
            accel = 0.0
            long_frict = self.crossFrict
        else:
            accel = dir * self.carAccel[car_state.type] * car_state.engine_power
            long_frict = self.longFrict

        angSpd = car_state.angular_speed
        baseAngSpd = car_state.angular_speed  # APPROXIMATELY. WORK ONLY IF WE HAD NO BUMPINGS

        angSpd -= baseAngSpd  # <-- problemous substraction
        baseAngSpd = self.carRotFactor * car_state.wheel_turn * np.dot(spd, dir)
        angSpd += baseAngSpd


        for i in xrange(Physics.PHYS_ITER):
            pos += spd * Physics.PHYS_DT
            spd += accel
            spd *= self.frictMul
            orthog_dir = np.array([-dir[1], dir[0]])
            spd -= limit(np.dot(spd, dir), long_frict) * dir + \
                   limit(np.dot(spd, orthog_dir), self.crossFrict) * orthog_dir

            angle += angSpd * Physics.PHYS_DT
            dir = np.array([cos(angle), sin(angle)])
            angSpd = baseAngSpd + (angSpd - baseAngSpd) * self.rotFrictMul

        car_state.angle = angle
        car_state.speed = spd
        car_state.angular_speed = angSpd
        car_state.pos = pos

        return car_state

    def calc_brake_distance(self, car_state_, speed_limit):
        car_state = copy.deepcopy(car_state_)
        car_state.brake = True
        start_pos = copy.deepcopy(car_state.pos)
        dir = np.array([cos(car_state.angle), sin(car_state.angle)])
        speed = get_speed_projection(car_state.speed[0], car_state.speed[1], dir)
        ticks = 0
        while speed > speed_limit:
            car_state = self.calc(car_state)
            dir = np.array([cos(car_state.angle), sin(car_state.angle)])
            speed = get_speed_projection(car_state.speed[0], car_state.speed[1], dir)
            ticks += 1
        brake_dist = distance.euclidean(start_pos, car_state.pos)
        return ticks, brake_dist, car_state


def demo_calc():
    import debug.ObjectLoader
    me, world, game = debug.ObjectLoader.load_objects()
    print world.map_name

    ticks = 474 - 180
    coord_180 = (6800.0, 7834.0)
    coord_474 = (992.637980, 7834.000000)
    v_180 = 0.0
    ep_180 = 1.0
    limit_ep = 1.0

    path_length, speed, cur_power = calc_path_rude(v_180, ep_180, limit_ep, ticks)
    print 'path_length(%.6f), speed(%.9f), EP(%.9f)' % (path_length, speed, cur_power)

    phys = Physics(world, game)
    me.engine_power = 1.0
    me.wheel_turn = 0
    me.speed_x = me.speed_y = 0.0
    car_state = CarState.from_car(me)

    for i in xrange(181, 475):
        car_state = phys.calc(car_state)
        print '[%d]' % i
        print car_state

def demo_calc_brake_distance():
    import debug.ObjectLoader
    me, world, game = debug.ObjectLoader.load_objects()
    phys = Physics(world, game)
    car_state = CarState.from_car(me)
    car_state.wheel_turn = 0.0
    car_state.speed = np.array([-39.0311463976256405, 0.0])
    speed_limit = 23.0
    ticks, brake_dist, car_state = phys.calc_brake_distance(car_state, speed_limit)
    print 'Ticks to break: %f Brake distance: %.16f' % (ticks, brake_dist)
    print car_state



if __name__ == '__main__':
    demo_calc_brake_distance()