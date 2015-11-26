from model.Car import Car
from model.Game import Game
from model.Move import Move
from model.World import World
import pickle
from MyCar import MyCar

class DebugStrategy:

     def __init__(self):
         self.mycar = None
         self.speed_list = None
         self.brake = False

     def move(self, me, world, game, move):
        """
        @type me: Car
        @type world: World
        @type game: Game
        @type move: Move
        """
        ##################
        # if world.tick == 0:
        #     with open('/home/artem/workspace/ai_cup/python2-cgdk/data/game_objects.bin', 'wb') as output:
        #         pickle.dump(me, output, pickle.HIGHEST_PROTOCOL)
        #         pickle.dump(world, output, pickle.HIGHEST_PROTOCOL)
        #         pickle.dump(game, output, pickle.HIGHEST_PROTOCOL)

        self.mycar = MyCar(me, game.track_tile_size)

        print 'Tick[%d] TILE%s ' % (world.tick, str(self.mycar.cur_tile))
        print 'P(%.16f, %.16f)  V(%.16f, %.16f) V_HYP(%.16f)' % (self.mycar.base.x, self.mycar.base.y, me.speed_x, me.speed_y, self.mycar.speed)
        print 'ANG(%.16f) ANG_V(%.16f)' % (me.angle, self.mycar.base.angular_speed)
        print 'EP(%.16f) WT(%.16f)' % (me.engine_power, me.wheel_turn)
        print 'PRJCT(%d)' % (me.projectile_count)

        move.engine_power = 1.0

        move.use_nitro = True
        if self.mycar.speed > 27.0:
            print 'START BRAKING!'
            self.brake = True

        move.brake = self.brake
        print 'BRAKE(%d)', move.brake
