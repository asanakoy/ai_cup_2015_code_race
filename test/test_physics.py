from unittest import TestCase
from debug.ObjectLoader import *
from debug.physics import Physics
from CarState import CarState
import numpy as np

__author__ = 'artem'


class TestPhysics(TestCase):

    def test_straight_movement(self):
        me, world, game = load_objects()

        phys = Physics(world, game)
        me.engine_power = 1.0
        me.wheel_turn = 0.0
        me.speed_x = me.speed_y = 0.0
        me.x = 6800.0
        me.y = 7834.0
        me.brake = False

        car_state_350 = CarState(3.1415926535897931,
                                 np.array([-23.8683149170807631, 0.0000000000000029]),
                                 0.0,
                                 np.array([4351.0112134403343589, 7834.0000000000000000]))

        car_state_474 = CarState(3.1415926535897931,
                                 np.array([-29.4477720000775669, 0.0000000000000036]),
                                 0.0,
                                 np.array([992.6379800312042789, 7834.0000000000000000]))

        for i in xrange(181, 475):
            car_state = phys.calc(me)
            car_state.update_car(me)
            if i == 350:
                self.assertEqual(car_state, car_state_350)
            elif i == 474:
                self.assertEqual(car_state, car_state_474)
