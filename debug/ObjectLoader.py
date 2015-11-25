from model.Car import Car
from model.Game import Game
from model.Move import Move
from model.World import World
import pickle
from MyCar import MyCar

OBJECTS_BIN_PATH = '/home/artem/workspace/ai_cup/python2-cgdk/data/game_objects.bin'

def load_objects(path=OBJECTS_BIN_PATH):

    with open(path, 'rb') as input_file:
        me = pickle.load(input_file)
        world = pickle.load(input_file)  # map09
        game = pickle.load(input_file)

    return me, world, game

