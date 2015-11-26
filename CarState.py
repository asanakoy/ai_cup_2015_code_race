import numpy as np
from model.CarType import CarType
__author__ = 'artem'

class CarState:

    def __init__(self, angle=None, speed=None, angular_speed=None, pos=None, wheel_turn=None,
                 engine_power=None, engine_power_lim=None, brake=False, _type=CarType.BUGGY):
        self.angle = angle
        self.speed = speed
        self.angular_speed = angular_speed
        self.pos = pos
        self.wheel_turn = wheel_turn
        self.engine_power = engine_power
        self.engine_power_lim = engine_power_lim
        self.brake = brake
        self.type = _type

    @classmethod
    def from_car(cls, car):
        obj = CarState(car.angle, np.array([car.speed_x, car.speed_y]), car.angular_speed,
                         np.array([car.x, car.y]), car.wheel_turn, car.engine_power)
        obj.type = car.type
        return obj

    def __str__(self):
        PREC = '.16'
        str = ('P(%' + PREC + 'f, %' + PREC + 'f)  V(%' + PREC + 'f, %' + PREC + 'f)\n') \
              % (self.pos[0], self.pos[1], self.speed[0], self.speed[1]) + \
              ('ANG(%' + PREC + 'f) ANG_V(%' + PREC + 'f)') % (self.angle, self.angular_speed)
        return str

    def __repr__(self):
        return str(self.__dict__)


    def __eq__(self, other):
        EPSILON = 1e-16
        return abs(self.angle - other.angle) < EPSILON and \
            np.allclose(self.speed, other.speed, rtol=0, atol=EPSILON) and \
            abs(self.angular_speed - other.angular_speed) < EPSILON and \
            np.allclose(self.pos, other.pos, rtol=0, atol=EPSILON)


    def update_car(self, car):
        car.angle = self.angle
        car.speed_x = self.speed[0]
        car.speed_y = self.speed[1]
        car.angular_speed = self.angular_speed
        car.x = self.pos[0]
        car.y = self.pos[1]