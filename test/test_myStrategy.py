from unittest import TestCase
from debug.ObjectLoader import *
from MyStrategy import MyStrategy
from model.Move import Move


class TestMyStrategy(TestCase):
    def test_move(self):
        me, world, game = load_objects()

        strategy = MyStrategy()
        move = Move()
        strategy.move(me, world, game, move)