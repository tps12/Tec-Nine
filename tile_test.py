from unittest import TestCase, main, skip

from tile import *

def layer(rock, thickness):
    return { 'rock': rock, 'thickness': thickness }

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
            (d[0], [layer(s[0], s[1]) for s in d[1]])
            for d in sourcedata]

        bottom, layers = Tile.mergelayers(sources)

        self.assertEqual(bottom, -35)

        layerdata = [(l.rock, l.thickness) for l in layers]
        self.assertEqual(layerdata, [(A, 9),(D,11),(A, 4),(D, 4),(A, 2),(B,18),(C,17)])

    def test_mergelayers_preserve_height(self):
        merged = Tile.mergelayers([(0, [layer('A', 1)]), (0, [layer('A', 2)])])
        self.assertEqual(merged[1][0].thickness, 2)

    def test_mergelayers_preserve_depth(self):
        merged = Tile.mergelayers([(-5, [layer('A', 10)]), (-2, [layer('A', 10)])])
        self.assertEqual(merged[0], -5)

    def test_mergelayers_most_common(self):
        merged = Tile.mergelayers([(0, [layer('A', 1)]), (0, [layer('B', 1)]), (0, [layer('B', 1)])])
        self.assertEqual(merged[1][0].rock, 'B')

    def test_mergelayers_prefer_change(self):
        merged = Tile.mergelayers([(0, [layer('A', 2)]),
                                   (0, [layer('B', 1), layer('A', 1)])])
        self.assertEqual(merged[1][0].rock, 'B')

    def test_mergelayers_most_common_trumps_change(self):
        merged = Tile.mergelayers([(0, [layer('A', 2)]),
                                   (0, [layer('A', 2)]),
                                   (0, [layer('B', 1), layer('A', 1)])])
        self.assertEqual(merged[1][0].rock, 'A')

    def test_mergelayers_prefer_first(self):
        merged = Tile.mergelayers([(0, [layer('A', 1), layer('D', 1), layer('G', 1)]),
                                   (0, [layer('B', 1), layer('E', 1), layer('H', 1)]),
                                   (0, [layer('C', 1), layer('F', 1), layer('I', 1)])])
        self.assertEqual([l.rock for l in merged[1]], ['A', 'D', 'G'])

    def test_mergelayers_prefer_first_among_most_common(self):
        merged = Tile.mergelayers([(0, [layer('A', 1), layer('D', 1), layer('G', 1)]),
                                   (0, [layer('A', 1), layer('D', 1), layer('G', 1)]),
                                   (0, [layer('B', 1), layer('E', 1), layer('H', 1)]),
                                   (0, [layer('B', 1), layer('E', 1), layer('H', 1)]),
                                   (0, [layer('C', 1), layer('F', 1), layer('I', 1)])])
        self.assertEqual([l.rock for l in merged[1]], ['A', 'D', 'G'])

    def test_mergelayers_identity(self):
        merged = Tile.mergelayers([(0, [layer('A', 1), layer('B', 1), layer('C', 1)])])
        self.assertEqual(merged, (0, [Layer('A', 1), Layer('B', 1), Layer('C', 1)]))

    class Material(object):
        def __init__(self, amount, total, substance):
            self.amount = amount
            self.total = total
            self.substance = substance

    def test_depositmaterials_thickness(self):
        deposit = Tile.depositmaterials([self.Material(1, 1, (0, [layer({}, 1)]))])
        self.assertEqual(deposit.thickness, 1)

    def test_depositmaterials_rock_type(self):
        deposit = Tile.depositmaterials([self.Material(1, 1, (0, [layer({}, 1)]))])
        self.assertEqual(deposit.rock['type'], 'S')

    def test_depositmaterials_amount(self):
        deposit = Tile.depositmaterials([self.Material(1, 2, (0, [layer({}, 2)]))])
        self.assertEqual(deposit.thickness, 1)

    def test_depositmaterials_amount_multiple_layers(self):
        deposit = Tile.depositmaterials([self.Material(1, 2, (0, [layer({}, 2), layer({}, 2)]))])
        self.assertEqual(deposit.thickness, 1)

    def test_depositmaterials_attributes(self):
        deposit = Tile.depositmaterials([self.Material(1, 1, (0, [layer({'something': 5}, 1)]))])
        self.assertTrue('something' in deposit.rock)
        self.assertEqual(deposit.rock['something'], 5)

    def test_depositmaterials_combine_attributes(self):
        deposit = Tile.depositmaterials([self.Material(2, 2, (0, [layer({'something': 5}, 1), layer({'something else': 5}, 1)]))])
        self.assertTrue('something' in deposit.rock)
        self.assertTrue('something else' in deposit.rock)

    def test_depositmaterials_average_attributes(self):
        deposit = Tile.depositmaterials([self.Material(2, 2, (0, [layer({'something': 5}, 1), layer({'something': 10}, 1)]))])
        self.assertEqual(deposit.rock['something'], 7.5)

    def test_depositmaterials_proportional_attributes(self):
        deposit = Tile.depositmaterials([self.Material(3, 3, (0, [layer({'something': 3}, 2), layer({'something': 6}, 1)]))])
        self.assertEqual(deposit.rock['something'], 4)

    def test_depositmaterials_top_attributes(self):
        deposit = Tile.depositmaterials([self.Material(1, 1, (0, [layer({'something': 5}, 1), layer({'something': 10}, 1)]))])
        self.assertEqual(deposit.rock['something'], 10)

    def test_depositmaterials_thickness_multiple_materials(self):
        deposit = Tile.depositmaterials([self.Material(1, 1, (0, [layer({}, 1)])),
                                         self.Material(1, 1, (0, [layer({}, 1)]))])
        self.assertEqual(deposit.thickness, 2)

    def test_depositmaterials_rock_type_multiple_materials(self):
        deposit = Tile.depositmaterials([self.Material(1, 1, (0, [layer({}, 1)])),
                                         self.Material(1, 1, (0, [layer({}, 1)]))])
        self.assertEqual(deposit.rock['type'], 'S')

    def test_depositmaterials_attributes_multiple_materials(self):
        deposit = Tile.depositmaterials([self.Material(1, 1, (0, [layer({'something': 5}, 1)])),
                                         self.Material(1, 1, (0, [layer({'something else': 10}, 1)]))])
        self.assertTrue('something' in deposit.rock)
        self.assertTrue('something else' in deposit.rock)

    def test_depositmaterials_average_attributes_multiple_materials(self):
        deposit = Tile.depositmaterials([self.Material(1, 1, (0, [layer({'something': 5}, 1)])),
                                         self.Material(1, 1, (0, [layer({'something': 10}, 1)]))])
        self.assertEqual(deposit.rock['something'], 7.5)

    def test_depositmaterials_proportional_attributes_multiple_materials(self):
        deposit = Tile.depositmaterials([self.Material(1, 1, (0, [layer({'something': 3}, 1)])),
                                         self.Material(2, 2, (0, [layer({'something': 6}, 2)]))])
        self.assertEqual(deposit.rock['something'], 5)

if __name__ == '__main__':
    main()
