from unittest import TestCase, main, skip

from rock import metamorphic

def layer(rock, thickness):
    return { 'rock': rock, 'thickness': thickness }

class MetamorphicTestCase(TestCase):
    def test_transform_succeeds(self):
        metamorphic.transform([layer({}, 50)])

    def test_transform_preserves_thickness(self):
        layers = metamorphic.transform([layer({}, 50)])
        self.assertEqual(sum([l['thickness'] for l in layers]), 50)

    def test_transform_leaves_top_alone(self):
        layers = metamorphic.transform([layer({ 'type': 'X' }, 50)])
        self.assertEqual(layers[-1]['rock']['type'], 'X')

    def test_transform_non_clastic_zeolite(self):
        layers = metamorphic.transform([layer({ 'type': 'X' }, 50)])
        self.assertEqual(layers[-2]['rock']['type'], 'X')

    def test_transform_gravelly_zeolite(self):
        layers = metamorphic.transform([layer({ 'clasticity': 0.5 }, 50)])
        self.assertEqual(layers[-2]['rock']['name'], 'psephite')

    def test_transform_sandy_zeolite(self):
        layers = metamorphic.transform([layer({ 'clasticity': 4 }, 50)])
        self.assertEqual(layers[-2]['rock']['name'], 'psammite')

    def test_transform_clayey_zeolite(self):
        layers = metamorphic.transform([layer({ 'clasticity': 32 }, 50)])
        self.assertEqual(layers[-2]['rock']['name'], 'pelite')

    def test_transform_blueschist(self):
        layers = metamorphic.transform([layer({ 'type': 'X' }, 50)])
        self.assertEqual(layers[-3]['rock']['name'], 'schist')

if __name__ == '__main__':
    main()
