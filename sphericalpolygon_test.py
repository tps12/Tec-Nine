from unittest import TestCase, main

from sphericalpolygon import *

class SphericalPolygonTestCase(TestCase):

    def test_kansas_in_us(self):
        p = SphericalPolygon([(48.60, -124.06),
                              (47.96, -89.17),
                              (41.50, -81.71),
                              (47.22, -68.73),
                              (44.56, -67.10),
                              (30.26, -82.53),
                              (32.47, -117.20)])
        self.assertTrue(p.contains((38.62, -98.62)))
                              
    def test_alberta_outside_us(self):          
        p = SphericalPolygon([(48.60, -124.06),
                              (47.96, -89.17),
                              (41.50, -81.71),
                              (47.22, -68.73),
                              (44.56, -67.10),
                              (30.26, -82.53),
                              (32.47, -117.20)])
        self.assertFalse(p.contains((53.49, -113.64)))
                             
if __name__ == '__main__':
    main()
