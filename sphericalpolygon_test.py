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

    def test_point_that_should_be_in(self):
        p = SphericalPolygon([(-0.29969773, -0.59342746, -0.74701079),
                              (-0.46959975, -0.60570495, -0.64233759), 
                              (-0.5404975 , -0.60307641, -0.58665262), 
                              (-0.52111863, -0.68835311, -0.50458435), 
                              (-0.41479604, -0.73683772, -0.53386742), 
                              (-0.41047578, -0.81103224, -0.41681692), 
                              (-0.22731679, -0.87585997, -0.42567169), 
                              (-0.09276682, -0.84144483, -0.53232031), 
                              (-0.04855812, -0.84643477, -0.53027379)])
        self.assertTrue(p.contains((-0.25916403755485623, -0.7554155674506348, -0.6018150231520483)))

    def test_another_point_that_should_be_in(self):
        p = SphericalPolygon([( 0.07826526, -0.8631922 , -0.49877228),
                              ( 0.00398304, -0.94347847, -0.33140987), 
                              (-0.02999477, -0.96742597, -0.25137087), 
                              ( 0.06420691, -0.9818318 , -0.17856034), 
                              ( 0.16057571, -0.95586931, -0.24602703), 
                              ( 0.24508727, -0.95988891, -0.13618192), 
                              ( 0.40681028, -0.88751077, -0.21640245), 
                              ( 0.44190865, -0.81611357, -0.37239145), 
                              ( 0.47401636, -0.79000325, -0.38884876)])
        self.assertTrue(p.contains((0.29210493879571187, -0.8867057671346513, -0.35836794954530027)))
                             
if __name__ == '__main__':
    main()
