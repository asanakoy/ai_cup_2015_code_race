__author__ = 'artem'

# from model.Car import Car
# from model.Game import Game
# from model.Move import Move
# from model.World import World
# from model.TileType import TileType
# from math import *
# from pprint import pprint
# from random import random
# import numpy as np


def sign(a):
    return (a > 0) - (a < 0)


def calc_path(v_0, car_power_0, limit_car_power, t):
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
        print 'cur_power', cur_power
        a = cur_power * (buggy_engine_forward_power if cur_power > 0 else -buggy_engine_rear_power)
        speed += a
        path_length += speed

    return path_length, speed, cur_power

