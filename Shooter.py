from math import *
import numpy as np
from model.TileType import TileType

__author__ = 'artem'


def should_shoot(me, world, game):
    """
    :type me: Mycar
    :type world: model.World
    :type game: model.Game
    """
    if world.tick <= game.initial_freeze_duration_ticks or me.base.projectile_count == 0 or me.base.remaining_projectile_cooldown_ticks > 0:
        return False

    EPSILON = 1e-16
    world_size = (world.width, world.height)

    my_dir = np.array(me.direction_vector)
    for i in xrange(2):
            my_dir[i] = 0.0 if abs(my_dir[i]) < EPSILON else my_dir[i]

    F_1 = me.base.x * my_dir[1] - me.base.y * my_dir[0]

    for car in world.cars:
        if not car.teammate and car.durability > 0 and not car.finished_track:

            #  simple close case
            if abs(me.base.get_angle_to_unit(car)) < pi / 90 and me.base.get_distance_to_unit(car) < 1.6 * game.track_tile_size:
                return True

            if abs(me.base.angle - car.angle) < EPSILON or car.engine_power > 1.0:
                continue

            dir = np.array([cos(car.angle), sin(car.angle)])
            for i in xrange(2):
                dir[i] = 0.0 if abs(dir[i]) < EPSILON else dir[i]

            if (my_dir[1] == 0.0 and dir[1] == 0.0 and me.base.y == car.y) or (my_dir[0] == 0.0 and dir[0] == 0.0 and me.base.x == car.x):
                if abs(me.base.get_angle_to_unit(car)) < pi / 90 and me.base.get_distance_to_unit(car) < 5.0 * game.track_tile_size:
                    return True
                else:
                    continue

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

            meet_tile = (int(floor(meet_point[0] / game.track_tile_size)),  int(floor(meet_point[1] / game.track_tile_size)))
            is_out_of_bounds = False
            for i in xrange(2):
                if meet_tile[i] < 0 or meet_tile[i] >= world_size[i]:
                    is_out_of_bounds = True
                    break
            if is_out_of_bounds:
                print 'Shoot? meet tile out of bounds (%s)' % str(meet_tile)
                continue

            meet_tile_type = world.tiles_x_y[meet_tile[0]][meet_tile[1]]

            target_speed_module = hypot(car.speed_x, car.speed_y)

            v1 = np.array([meet_point[0] - me.base.x, meet_point[1] - me.base.y])
            v1 /= np.linalg.norm(v1)
            v2 = np.array([meet_point[0] - car.x, meet_point[1] - car.y])
            v2 /= np.linalg.norm(v2)

            L_1 = me.base.get_distance_to(meet_point[0], meet_point[1])
            L_2 = car.get_distance_to(meet_point[0], meet_point[1])

            time = L_1 / game.washer_initial_speed
            max_speed = 30.5
            time_to_accelerate = min(time, (max_speed - target_speed_module) / 0.25)
            enemy_path = (2.0 * target_speed_module + time_to_accelerate * 0.25) / 2.0 * time_to_accelerate
            if time - time_to_accelerate > 0:
                enemy_path += (time - time_to_accelerate) * max_speed

            # TODO make more accurate path approximation

            #############
            print 'Shoot?'
            print 'time (%.2f), time_to_accelerate (%.2f)' % (time, time_to_accelerate)
            print 'np.dot(v1, my_dir) > 0.0 and np.dot(v2, dir) > 0.0',  np.dot(v1, my_dir) > 0.0 and np.dot(v2, dir) > 0.0
            print 'L1 (%.2f) L2 (%.2f) enemy_path(%.2f), MEET_TILE_TYPE: (%d)' % (L_1, L_2, enemy_path, meet_tile_type)
            print 'Target: hp(%.2f) WT(%.2f) SP_MODULE(%.2f) ANGLE(%.2f)' % (car.durability, car.wheel_turn, target_speed_module, car.angle)

            #############

            if np.dot(v1, my_dir) > 0.0 and np.dot(v2, dir) > 0.0 and target_speed_module > 9.0 \
                    and L_1 < game.track_tile_size * 6.0 and (enemy_path - 35) <= L_2 <= (enemy_path + 35) and \
                    (abs(car.wheel_turn) < 0.3 or enemy_path < 1.0 * game.track_tile_size) and \
                    meet_tile_type != TileType.UNKNOWN and meet_tile_type != TileType.EMPTY:
                return True
            else:
                pass

    return False

