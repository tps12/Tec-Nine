from unittest import TestCase, main, skip

from rock import sedimentary

def layer(rock, thickness):
    return { 'rock': rock, 'thickness': thickness }

class SedimentaryTestCase(TestCase):
    class Material(object):
        def __init__(self, amount, total, substance):
            self.amount = amount
            self.total = total
            self.substance = substance

    def test_depositmaterials_thickness(self):
        deposit = sedimentary.deposit([self.Material(1, 1, [layer({}, 1)])], False, False, None)
        self.assertEqual(deposit['thickness'], 1)

    def test_depositmaterials_rock_type(self):
        deposit = sedimentary.deposit([self.Material(1, 1, [layer({}, 1)])], False, False, None)
        self.assertEqual(deposit['rock']['type'], 'S')

    def test_depositmaterials_amount(self):
        deposit = sedimentary.deposit([self.Material(1, 2, [layer({}, 2)])], False, False, None)
        self.assertEqual(deposit['thickness'], 1)

    def test_depositmaterials_amount_multiple_layers(self):
        deposit = sedimentary.deposit([self.Material(1, 2, [layer({}, 2), layer({}, 2)])], False, False, None)
        self.assertEqual(deposit['thickness'], 1)

    def test_depositmaterials_attributes(self):
        deposit = sedimentary.deposit([self.Material(1, 1, [layer({'something': 5}, 1)])], False, False, None)
        self.assertTrue('something' in deposit['rock'])
        self.assertEqual(deposit['rock']['something'], 5)

    def test_depositmaterials_combine_attributes(self):
        deposit = sedimentary.deposit([self.Material(2, 2, [layer({'something': 5}, 1), layer({'something else': 5}, 1)])], False, False, None)
        self.assertTrue('something' in deposit['rock'])
        self.assertTrue('something else' in deposit['rock'])

    def test_depositmaterials_average_attributes(self):
        deposit = sedimentary.deposit([self.Material(2, 2, [layer({'something': 5}, 1), layer({'something': 10}, 1)])], False, False, None)
        self.assertEqual(deposit['rock']['something'], 7.5)

    def test_depositmaterials_proportional_attributes(self):
        deposit = sedimentary.deposit([self.Material(3, 3, [layer({'something': 3}, 2), layer({'something': 6}, 1)])], False, False, None)
        self.assertEqual(deposit['rock']['something'], 4)

    def test_depositmaterials_top_attributes(self):
        deposit = sedimentary.deposit([self.Material(1, 1, [layer({'something': 5}, 1), layer({'something': 10}, 1)])], False, False, None)
        self.assertEqual(deposit['rock']['something'], 10)

    def test_depositmaterials_thickness_multiple_materials(self):
        deposit = sedimentary.deposit([self.Material(1, 1, [layer({}, 1)]),
                                       self.Material(1, 1, [layer({}, 1)])],
                                       False, False, None)
        self.assertEqual(deposit['thickness'], 2)

    def test_depositmaterials_rock_type_multiple_materials(self):
        deposit = sedimentary.deposit([self.Material(1, 1, [layer({}, 1)]),
                                       self.Material(1, 1, [layer({}, 1)])],
                                       False, False, None)
        self.assertEqual(deposit['rock']['type'], 'S')

    def test_depositmaterials_attributes_multiple_materials(self):
        deposit = sedimentary.deposit([self.Material(1, 1, [layer({'something': 5}, 1)]),
                                       self.Material(1, 1, [layer({'something else': 10}, 1)])],
                                       False, False, None)
        self.assertTrue('something' in deposit['rock'])
        self.assertTrue('something else' in deposit['rock'])

    def test_depositmaterials_average_attributes_multiple_materials(self):
        deposit = sedimentary.deposit([self.Material(1, 1, [layer({'something': 5}, 1)]),
                                       self.Material(1, 1, [layer({'something': 10}, 1)])],
                                       False, False, None)
        self.assertEqual(deposit['rock']['something'], 7.5)

    def test_depositmaterials_proportional_attributes_multiple_materials(self):
        deposit = sedimentary.deposit([self.Material(1, 1, [layer({'something': 3}, 1)]),
                                       self.Material(2, 2, [layer({'something': 6}, 2)])],
                                       False, False, None)
        self.assertEqual(deposit['rock']['something'], 5)

if __name__ == '__main__':
    main()
