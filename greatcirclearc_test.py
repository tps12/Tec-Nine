from unittest import TestCase, main

from math import pi, cos, sin

from greatcirclearc import *

class GreatCircleArcTestCase(TestCase):

    @staticmethod
    def vector(p):
        cos_lat = cos(p[0] * pi/180)
        return (cos_lat * cos(p[1] * pi/180),
                cos_lat * sin(p[1] * pi/180),
                sin(p[0] * pi/180))

    def test_only_one_of_these_should_intersect(self):
        count = 0

        arc = GreatCircleArc((0.29210493879571187, -0.8867057671346513, -0.35836794954530027), (-0.21032302, 0.93088621, 0.29868896))
        for other in (GreatCircleArc((0.47401636, -0.79000325, -0.38884876), (0.07826526, -0.8631922, -0.49877228)),
                      GreatCircleArc((-0.02999477, -0.96742597, -0.25137087), (0.06420691, -0.9818318, -0.17856034))):
            if arc.intersects(other):
                count += 1
        
        self.assertEqual(count, 1)
                   
if __name__ == '__main__':
    main()
