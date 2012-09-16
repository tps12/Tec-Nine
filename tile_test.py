from unittest import TestCase, main, skip

from tile import *

class TileTestCase(TestCase):

    def test_mergelayers(self):
        # contrived example, but includes:
        #  - regions above and below where only 1 or 2 sources have a definition
        #  - regions where two sources outvote the third
        #  - toss-up regions that should grab the unique layer
        A = 'A'
        B = 'B'
        C = 'C'
        D = 'D'
        E = 'E'

        sourcedata = [
            (-15, [(A,10),(B,18),(C,10)]),
            (-35, [(A, 9),(D,27),(B, 7),(E,10),(C,12)]),
            (-18, [(A, 7),(E, 4),(B,10),(C,17)])
        ]

        sources = [
            (d[0], [Layer(s[0], s[1]) for s in d[1]])
            for d in sourcedata]

        bottom, layers = Tile.mergelayers(sources)

        self.assertEqual(bottom, -35)

        layerdata = [(l.rock, l.thickness) for l in layers]
        self.assertEqual(layerdata, [(A, 9),(D,11),(A, 4),(D, 4),(A, 2),(B,18),(C,17)])

    def test_mergelayers_preserve_height(self):
        merged = Tile.mergelayers([(0, [Layer('A', 1)]), (0, [Layer('A', 2)])])
        self.assertEqual(merged[1][0].thickness, 2)

    def test_mergelayers_preserve_depth(self):
        merged = Tile.mergelayers([(-5, [Layer('A', 10)]), (-2, [Layer('A', 10)])])
        self.assertEqual(merged[0], -5)

    def test_mergelayers_most_common(self):
        merged = Tile.mergelayers([(0, [Layer('A', 1)]), (0, [Layer('B', 1)]), (0, [Layer('B', 1)])])
        self.assertEqual(merged[1][0].rock, 'B')

    def test_mergelayers_prefer_change(self):
        merged = Tile.mergelayers([(0, [Layer('A', 2)]),
                                   (0, [Layer('B', 1), Layer('A', 1)])])
        self.assertEqual(merged[1][0].rock, 'B')

    def test_mergelayers_most_common_trumps_change(self):
        merged = Tile.mergelayers([(0, [Layer('A', 2)]),
                                   (0, [Layer('A', 2)]),
                                   (0, [Layer('B', 1), Layer('A', 1)])])
        self.assertEqual(merged[1][0].rock, 'A')

    def test_mergelayers_prefer_first(self):
        merged = Tile.mergelayers([(0, [Layer('A', 1), Layer('D', 1), Layer('G', 1)]),
                                   (0, [Layer('B', 1), Layer('E', 1), Layer('H', 1)]),
                                   (0, [Layer('C', 1), Layer('F', 1), Layer('I', 1)])])
        self.assertEqual([l.rock for l in merged[1]], ['A', 'D', 'G'])

    def test_mergelayers_prefer_first_among_most_common(self):
        merged = Tile.mergelayers([(0, [Layer('A', 1), Layer('D', 1), Layer('G', 1)]),
                                   (0, [Layer('A', 1), Layer('D', 1), Layer('G', 1)]),
                                   (0, [Layer('B', 1), Layer('E', 1), Layer('H', 1)]),
                                   (0, [Layer('B', 1), Layer('E', 1), Layer('H', 1)]),
                                   (0, [Layer('C', 1), Layer('F', 1), Layer('I', 1)])])
        self.assertEqual([l.rock for l in merged[1]], ['A', 'D', 'G'])

    def test_mergelayers_identity(self):
        merged = Tile.mergelayers([(0, [Layer('A', 1), Layer('B', 1), Layer('C', 1)])])
        self.assertEqual(merged, (0, [Layer('A', 1), Layer('B', 1), Layer('C', 1)]))

if __name__ == '__main__':
    main()
