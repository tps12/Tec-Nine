from math import cos, sin

from numpy import cross
from numpy.linalg import norm

from sphericalpolygon import *

class Shape(object):
    def __init__(self, coords, location, orientation, velocity):
        self._coords = [c for c in coords]
        self._location = location
        self._orientation = orientation
        self._velocity = velocity

    @staticmethod
    def _rotate(p, axis, theta):
        # http://inside.mines.edu/~gmurray/ArbitraryAxisRotation/ArbitraryAxisRotation.html
        L2 = sum([i*i for i in axis])
        return array([(axis[0]*sum(p * axis) +
                       (p[0]*(axis[1]*axis[1]+axis[2]*axis[2]) +
                        axis[0]*(-axis[1]*p[1]-axis[2]*p[2])) * cos(theta) +
                       sqrt(L2)*(-axis[2]*p[1]+axis[1]*p[2]) * sin(theta))/L2,
                      (axis[1]*sum(p * axis) +
                       (p[1]*(axis[0]*axis[0]+axis[2]*axis[2]) +
                        axis[1]*(-axis[0]*p[0]-axis[2]*p[2])) * cos(theta) +
                       sqrt(L2)*(axis[2]*p[0]-axis[0]*p[2]) * sin(theta))/L2,
                      (axis[2]*sum(p * axis) +
                       (p[2]*(axis[0]*axis[0]+axis[1]*axis[1]) +
                        axis[2]*(-axis[0]*p[0]-axis[1]*p[1])) * cos(theta) +
                       sqrt(L2)*(-axis[1]*p[0]+axis[0]*p[1]) * sin(theta))/L2])
     
    def projection(self):
        u = cross(self._location, self._orientation)
        u = u / norm(u)

        vectors = []
        for (x,y) in self._coords:
            py = self._rotate(self._location, u, y)
            uy = cross(py, u)
            uy = uy / norm(uy)
            vectors.append(self._rotate(py, uy, x))
        return SphericalPolygon(vectors, self._location)

    def apply_velocity(self, dt):
        d = norm(self._velocity) * dt

        if d:
            axis = cross(self._location, self._velocity)
            axis = axis / norm(axis)

            self._location, self._orientation, self._velocity = [self._rotate(i, axis, d)
                                                                 for i in
                                                                 self._location,
                                                                 self._orientation,
                                                                 self._velocity]


