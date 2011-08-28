from unittest import TestCase, main

from math import pi, cos, sin

from sphericalpolygon import *

class SphericalPolygonTestCase(TestCase):

    @staticmethod
    def vector(p):
        cos_lat = cos(p[0] * pi/180)
        return (cos_lat * cos(p[1] * pi/180),
                cos_lat * sin(p[1] * pi/180),
                sin(p[0] * pi/180))

    def test_kansas_in_us(self):
        p = SphericalPolygon([self.vector(p) for p in
                              (48.60, -124.06),
                              (47.96, -89.17),
                              (41.50, -81.71),
                              (47.22, -68.73),
                              (44.56, -67.10),
                              (30.26, -82.53),
                              (32.47, -117.20)])
        self.assertTrue(p.contains(self.vector((38.62, -98.62))))
                              
    def test_alberta_outside_us(self):          
        p = SphericalPolygon([self.vector(p) for p in
                              (48.60, -124.06),
                              (47.96, -89.17),
                              (41.50, -81.71),
                              (47.22, -68.73),
                              (44.56, -67.10),
                              (30.26, -82.53),
                              (32.47, -117.20)])
        self.assertFalse(p.contains(self.vector((53.49, -113.64))))
                             
if __name__ == '__main__':
    main()
