__author__ = 'artem'

from math import *
from utils import *
from math_ex import *
from model.Car import Car

class MyCar:

    def __init__(self, car, track_tile_size):
        """
        @type car: Car
        """
        self.base = car
        self.direction_vector = (cos(car.angle), sin(car.angle))

        speed_module = hypot(car.speed_x, car.speed_y)
        speed_sign = sign(self.direction_vector[0] * car.speed_x + self.direction_vector[1] * car.speed_y)
        self.speed = speed_sign * speed_module
        self.cur_tile = (int(floor(car.x / track_tile_size)),  int(floor(car.y / track_tile_size)))



