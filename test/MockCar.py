
from model.Car import Car
from model.CarType import CarType
__author__ = 'artem'


class MockCar(Car):

    def __init__(self):
        #  Rectangular Unit args
        _id = 0
        mass = 1000
        x = 300
        y = 300
        speed_x = 0.0
        speed_y = 0.0
        angle = 0.0
        angular_speed = 0.0
        width = 120
        height = 140

        # Car args
        player_id = 0
        teammate_index = 0
        teammate = True
        type = CarType.BUGGY
        projectile_count = 0
        nitro_charge_count = 0
        oil_canister_count = 0
        remaining_projectile_cooldown_ticks = 0
        remaining_nitro_cooldown_ticks = 0
        remaining_oil_cooldown_ticks = 0
        remaining_nitro_ticks = 0
        remaining_oiled_ticks = 0
        durability = 100
        engine_power = 0.0
        wheel_turn = 0.0
        next_waypoint_index = 0
        next_waypoint_x = 0
        next_waypoint_y = 0
        finished_track = False

        Car.__init__(self, _id, mass, x, y, speed_x, speed_y, angle, angular_speed, width, height, player_id, teammate_index,
                 teammate, type, projectile_count, nitro_charge_count, oil_canister_count,
                 remaining_projectile_cooldown_ticks, remaining_nitro_cooldown_ticks, remaining_oil_cooldown_ticks,
                 remaining_nitro_ticks, remaining_oiled_ticks, durability, engine_power, wheel_turn,
                 next_waypoint_index, next_waypoint_x, next_waypoint_y, finished_track)
