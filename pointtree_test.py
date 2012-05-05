from unittest import TestCase, main

from pointtree import *

class PointTreeTestCase(TestCase):

    def test_constructor(self):
        PointTree((0,0), (1,1))

    def test_requires_two_points(self):
        self.assertRaises(ValueError, PointTree, (0,0))

    def test_dimensions_must_match(self):
        self.assertRaises(ValueError, PointTree, (0,0), (1,1,1))

    def test_1d(self):
        PointTree(1, 2, 3)

    def test_requires_numbers(self):
        self.assertRaises(ValueError, PointTree, ('a','b'), ('x','y'))

    def test_infinite_branch(self):
        # figure out length required to cause branch
        count = 2
        while PointTree(*range(count)).depth() < 2:
            count += 1
        # create a tree with uniform values to try to force infinite recursion
        PointTree(*[0 for i in range(count)])

    def test_empty_branch(self):
        ps = [(0,0), (1,0), (0,1)]
        args = list(ps)
        dl = 0.01
        i = 1
        while PointTree(*args).depth() < 2:
            idl = i * dl
            args += [(idl,idl), (1-idl,idl), (idl,1-idl)]
            i += 1

    def test_nearest(self):
        t = PointTree(0, 1, 2, 3, 4, 5)
        self.assertEqual(t.nearest(0.75, 3), [1, 0, 2])

    def test_nearest_across_boundary(self):
        t = PointTree(0, 1, 2, 3, 4, 5)
        self.assertEqual(t.nearest(3.25, 3), [3, 4, 2])

    def test_2d(self):
        grid = """
            0         5        10
            + - - - - - - - - - + 0
            . o               o .
            .                   .
            .                   .
            .           1       .
            .                   . 5
            .       v   0       .
            .                   .
            .   2               .
            .                   .
            + - - - - - - - - - + 10
            """
        t = PointTree((1,1), (1,9), (4,6), (6,6), (8,2))
        self.longMessage = True
        self.assertEqual(t.nearest((6,4), 3), [(6,6), (4,6), (8,2)], msg=grid)

    def test_2d_across_boundary(self):
        grid = """
            0         5        10
            + - - - - + - - - - + 0
            . o       .       o .
            .         .         .
            .         .         .
            .         . 1       .
            + - - - - + - - - - + 5
            .       v . 0       .
            .         .         .
            .   2     .         .
            .         .         .
            + - - - - + - - - - + 10
            """
        args = [(1,1), (1,9), (4,6), (6,6), (8,2)]
        while True:
            t = PointTree(*args)
            if t.depth() > 1:
                break
            args += [(0,0), (9,9)]
        self.longMessage = True
        self.assertEqual(t.nearest((6,4), 3), [(6,6), (4,6), (8,2)], msg=grid)

if __name__ == '__main__':
    main()
