from unittest import TestCase, main, skip

from rock import metamorphic

def layer(rock, thickness):
    return { 'rock': rock, 'thickness': thickness }

class MetamorphicTestCase(TestCase):
    def test_regional_succeeds(self):
        metamorphic.regional([layer({}, 50)], True)

    def test_regional_preserves_thickness(self):
        layers = metamorphic.regional([layer({}, 50)], True)
        self.assertEqual(sum([l['thickness'] for l in layers]), 50)

    def test_regional_leaves_top_alone(self):
        layers = metamorphic.regional([layer({ 'type': 'X' }, 50)], True)
        self.assertEqual(layers[-1]['rock']['type'], 'X')

    def test_regional_non_clastic_zeolite(self):
        layers = metamorphic.regional([layer({ 'type': 'X' }, 50)], True)
        self.assertEqual(layers[-2]['rock']['type'], 'X')

    def test_regional_gravelly_zeolite(self):
        layers = metamorphic.regional([layer({ 'clasticity': 0.5 }, 50)], True)
        self.assertEqual(layers[-2]['rock']['name'], 'psephite')

    def test_regional_sandy_zeolite(self):
        layers = metamorphic.regional([layer({ 'clasticity': 4 }, 50)], True)
        self.assertEqual(layers[-2]['rock']['name'], 'psammite')

    def test_regional_clayey_zeolite(self):
        layers = metamorphic.regional([layer({ 'clasticity': 32 }, 50)], True)
        self.assertEqual(layers[-2]['rock']['name'], 'pelite')

    def test_regional_blueschist(self):
        layers = metamorphic.regional([layer({ 'type': 'X' }, 50)], True)
        self.assertEqual(layers[-3]['rock']['name'], 'blueschist')

    def test_regional_eclogite(self):
        layers = metamorphic.regional([layer({ 'type': 'X' }, 75)], True)
        self.assertEqual(layers[-4]['rock']['name'], 'eclogite')

    def test_regional_greenschist(self):
        layers = metamorphic.regional([layer({ 'type': 'X' }, 50)], False)
        self.assertEqual(layers[-3]['rock']['name'], 'greenschist')

    def test_regional_amphibolite(self):
        layers = metamorphic.regional([layer({ 'type': 'X' }, 50)], False)
        self.assertEqual(layers[-4]['rock']['name'], 'amphibolite')

    def test_regional_nonsubduction_eclogite(self):
        layers = metamorphic.regional([layer({ 'type': 'X' }, 75)], False)
        self.assertEqual(layers[-5]['rock']['name'], 'eclogite')

    def test_contact_succeeds(self):
        metamorphic.contact([layer({}, 50)], (5, 6))

    def test_contact_leaves_top_alone(self):
        layers = metamorphic.contact([layer({ 'type': 'X' }, 50)], (5, 6))
        self.assertEqual(layers[-1]['rock']['type'], 'X')

    def test_contact_hornfels_above(self):
        layers = metamorphic.contact([layer({ 'type': 'X' }, 50)], (5, 6))
        self.assertEqual(layers[-2]['rock']['name'], 'hornfels')

    def test_contact_granulite_above(self):
        layers = metamorphic.contact([layer({ 'type': 'X' }, 50)], (5, 6))
        self.assertEqual(layers[-3]['rock']['name'], 'granulite')

    def test_contact_intrusion_left_alone(self):
        layers = metamorphic.contact([layer({ 'type': 'X' }, 50)], (5, 6))
        self.assertEqual(layers[-4]['rock']['type'], 'X')

    def test_contact_granulite_below(self):
        layers = metamorphic.contact([layer({ 'type': 'X' }, 50)], (5, 6))
        self.assertEqual(layers[-5]['rock']['name'], 'granulite')

    def test_contact_hornfels_below(self):
        layers = metamorphic.contact([layer({ 'type': 'X' }, 50)], (5, 6))
        self.assertEqual(layers[-6]['rock']['name'], 'hornfels')

    def test_deep_contact_no_granulite(self):
        layers = metamorphic.contact([layer({ 'type': 'X' }, 50)], (25, 26))
        self.assertEqual(layers[-2]['rock']['name'], 'hornfels')
        self.assertEqual(layers[-3]['rock']['type'], 'X')
        self.assertEqual(layers[-4]['rock']['name'], 'hornfels')

    def test_contact_aureole_depends_on_intrusion_size(self):
        thicklayers = metamorphic.contact([layer({ 'type': 'X' }, 50)], (5, 6))
        thinlayers = metamorphic.contact([layer({ 'type': 'X' }, 50)], (5.4, 5.6))
        self.assertLess(thinlayers[-2]['thickness'], thicklayers[-2]['thickness'])

if __name__ == '__main__':
    main()
