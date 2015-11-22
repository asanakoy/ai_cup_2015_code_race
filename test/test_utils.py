from unittest import TestCase
from utils import *

__author__ = 'artem'


class TestUtils(TestCase):

    def test_v_add_with_coeff(self):
        v1 = (1, 2)
        v2 = (3, 8)
        self.assertEqual(v_add_with_coeff(v1, v2, 1.0, 0.3), (1 + 0.3*3, 2 + 0.3 * 8))
        self.assertEqual(v_add_with_coeff(v1, v2, -1.0, 0.3), (-1 + 0.3*3, -2 + 0.3 * 8))

    def test_vector_add_substract(self):
        v1 = (1, 2)
        v2 = (3, 8)
        self.assertEqual(vector_add(v1, v2), (1 + 3, 2 + 8))
        self.assertEqual(vector_substract(v1, v2), (1 - 3, 2 - 8))
