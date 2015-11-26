from unittest import TestCase
import numpy as np

from debug.ObjectLoader import *
from physics import Physics
from CarState import CarState

__author__ = 'artem'


class TestPhysics(TestCase):
    EPSILON = 1e-15

    def test_straight_movement(self):
        me, world, game = load_objects()

        phys = Physics(world, game)
        me.speed_x = me.speed_y = 0.0
        me.x = 6800.0
        me.y = 7834.0
        car_state = CarState.from_car(me)
        car_state.brake = False
        car_state.engine_power = 1.0
        car_state.wheel_turn = 0.0

        car_state_350 = CarState(3.1415926535897931,
                                 np.array([-23.8683149170807631, 0.0000000000000029]),
                                 0.0,
                                 np.array([4351.0112134403343589, 7834.0000000000000000]))

        car_state_474 = CarState(3.1415926535897931,
                                 np.array([-29.4477720000775669, 0.0000000000000036]),
                                 0.0,
                                 np.array([992.6379800312042789, 7834.0000000000000000]))

        for i in xrange(181, 475):
            car_state = phys.calc(car_state)
            car_state.update_car(car_state)
            if i == 350:
                self.assertEqual(car_state, car_state_350)
            elif i == 474:
                self.assertEqual(car_state, car_state_474)

    def test_calc_brake_distance(self):
        me, world, game = load_objects()
        phys = Physics(world, game)
        car_state = CarState.from_car(me)
        car_state.wheel_turn = 0.0
        car_state.speed = np.array([-27.0311463976256405, 0.0])
        speed_limit = 1.8195814109630735
        ticks, brake_dist, car_state = phys.calc_brake_distance(car_state, speed_limit)
        self.assertEqual(ticks, 72)
        self.assertAlmostEquals(brake_dist, 958.2923150089691262, delta=TestPhysics.EPSILON)
        self.assertTrue(np.allclose(car_state.speed, np.array([-1.8195814109630735, 0.0]),
                                    rtol=0, atol=TestPhysics.EPSILON))
