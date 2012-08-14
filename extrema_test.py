from unittest import TestCase, main

from extrema import *

class ExtremaTestCase(TestCase):

    def test_maximum(self):
        self.assertEqual(findextrema([1,2,3,2,1], lambda a, b: a > b), [2])

    def test_minimum(self):
        self.assertEqual(findextrema([3,2,1,2,3], lambda a, b: a < b), [2])

    def test_maxima(self):
        self.assertEqual(findextrema([1,2,1,2,3,2,1], lambda a, b: a > b), [1,4])

    def test_adjacent(self):
        self.assertEqual(findextrema([1,2,2,1], lambda a, b: a > b), [1,2])

    def test_wrap(self):
        self.assertEqual(findextrema([2,1,2,3], lambda a, b: a > b), [3])

    def test_adjacent_wrap(self):
        self.assertEqual(findextrema([3,2,1,2,3], lambda a, b: a > b), [0,4])

    def test_2(self):
        self.assertEqual(findextrema([1,2], lambda a, b: a > b), [1])

    def test_1(self):
        self.assertEqual(findextrema([1], lambda a, b: a > b), [0])

    def test_0(self):
        self.assertRaises(ValueError, findextrema, [], lambda a, b: a > b)

    def test_uniform(self):
        self.assertEqual(findextrema([1,1,1], lambda a, b: a > b), [])

    def test_best_last(self):
        self.assertEqual(findextrema([1,2,3], lambda a, b: a > b), [2])

    def test_best_first(self):
        self.assertEqual(findextrema([3,2,1], lambda a, b: a > b), [0])

    def test_best_second_last(self):
        self.assertEqual(findextrema([1,2,3,2], lambda a, b: a > b), [2])

    def test_best_second(self):
        self.assertEqual(findextrema([2,3,2,1], lambda a, b: a > b), [1])

    def test_this_error_case(self):
        # an actual bad response
        self.assertEqual(findextrema([0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 1, 1, 1, 1, 1, 2, 3, 3, 4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 3, 4, 3, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], lambda a, b: a > b), [8, 9, 10, 50, 51, 52, 61, 127])

    def test_another_error_case(self):
        # distilled from above
        self.assertEqual(findextrema([0,1,2,2,2,1,1,0], lambda a, b: a > b), [2,3,4])

if __name__ == '__main__':
    main()
