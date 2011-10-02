from unittest import TestCase, main

from math import acos, pi, cos, sin

from numpy import dot

from greatcircle import *
from greatcirclearc import *

class GreatCircleArcTestCase(TestCase):

    def test_only_one_of_these_should_intersect(self):
        count = 0

        arc = GreatCircleArc((0.29210493879571187, -0.8867057671346513, -0.35836794954530027), (-0.21032302, 0.93088621, 0.29868896))
        for other in (GreatCircleArc((0.07826526, -0.8631922, -0.49877228), (0.47401636, -0.79000325, -0.38884876)),
                      GreatCircleArc((-0.02999477, -0.96742597, -0.25137087), (0.06420691, -0.9818318, -0.17856034))):
            if arc.intersects(other):
                count += 1
        
        self.assertEqual(count, 1)
                   
    def test_less_than_hemisphere_should_not_contain_more_than_one_intersection(self):
        count = 0

        c = GreatCircle((0.29210493879571187, -0.8867057671346513, -0.35836794954530027), (-0.21032302, 0.93088621, 0.29868896))
        intersections = c.intersects(GreatCircle((0.47401636, -0.79000325, -0.38884876), (0.07826526, -0.8631922, -0.49877228)))

        arc = GreatCircleArc(c._start, c._end)
        self.assertTrue(acos(dot(arc._start, arc._end)) < pi)

        for intersection in intersections:
            if arc.contains(intersection):
                count += 1
        
        self.assertEqual(count, 1)

if __name__ == '__main__':
    main()
