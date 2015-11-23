from math import *
import numpy as np

__author__ = 'artem'


def should_shoot(me, world, game):
    """
    :type me: Mycar
    :type world: model.World
    :type game: model.Game
    """
    if world.tick <= game.initial_freeze_duration_ticks:
        return False

    my_dir = np.array(me.direction_vector)
    F_1 = me.base.x * my_dir[1] - me.base.y * my_dir[0]

    for car in world.cars:
        if not car.teammate and car.durability > 0:

            #  simple close case
            if abs(me.base.get_angle_to_unit(car)) < pi / 90 and me.base.get_distance_to_unit(car) < 1.6 * game.track_tile_size:
                return True

            dir = np.array([cos(car.angle), sin(car.angle)])

            if (my_dir[1] == 0.0 and dir[1] == 0.0 and me.base.y == car.y) or (my_dir[0] == 0.0 and dir[0] == 0.0 and me.base.x == car.x):
                if abs(me.base.get_angle_to_unit(car)) < pi / 90 and me.base.get_distance_to_unit(car) < 5.0 * game.track_tile_size:
                    return True
                else:
                    return False

            F_2 = car.x * dir[1] - car.y * dir[0]

            meet_point = [0, 0]
            if my_dir[1] == 0.0 and dir[0] == 0.0:
                meet_point[1] = me.base.y
                meet_point[0] = car.x
            elif my_dir[0] == 0.0 and dir[1] == 0.0:
                meet_point[1] = car.y
                meet_point[0] = me.base.x
            elif my_dir[0] == 0.0:
                meet_point[0] = me.base.x
                meet_point[1] = (dir[1] * meet_point[0] - F_2) / dir[0]
            elif my_dir[1] == 0.0:
                meet_point[1] = me.base.y
                meet_point[0] = (dir[0] * meet_point[1] + F_2) / dir[1]
            else:
                meet_point[1] = (dir[1] / my_dir[1] * F_1 - F_2) / (dir[0] - my_dir[0] * dir[1] / my_dir[1])
                meet_point[0] = (my_dir[0] * meet_point[1] + F_1) / my_dir[1]

            target_speed_module = hypot(car.speed_x, car.speed_y)

            v1 = np.array([meet_point[0] - me.base.x, meet_point[1] - me.base.y])
            v1 /= np.linalg.norm(v1)
            v2 = np.array([meet_point[0] - car.x, meet_point[1] - car.y])
            v2 /= np.linalg.norm(v2)

            L_1 = me.base.get_distance_to(meet_point[0], meet_point[1])
            L_2 = car.get_distance_to(meet_point[0], meet_point[1])

            time = L_1 / game.washer_initial_speed
            enemy_path = (2.0 * target_speed_module + time * 0.25) / 2.0 * time
            # TODO make more accurate path approximation

            if np.dot(v1, my_dir) > 0.0 and np.dot(v2, dir) > 0.0 and target_speed_module > 9.0 \
                    and L_1 < game.track_tile_size * 6.0 and (enemy_path - 35) <= L_2 <= (enemy_path + 35):
                return True

    return False

