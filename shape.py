from math import acos, cos, sin, pi
from random import randint

from numpy import array, cross
from numpy.linalg import norm

from shapely.geometry import Polygon

from sphericalpolygon import *

class Shape(object):
    def __init__(self, coords, location, orientation, velocity):
        self._polygon = Polygon(coords)
        self._location = location
        self._orientation = orientation
        self._velocity = velocity
        self._history = []

    @staticmethod
    def _rotate(p, axis, theta):
        """Rotate a vector about an axis by a specified amount."""
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

    def split(self):
        """Split the shape into two child shapes."""
        c = self._polygon.centroid.coords[0]
        cs = self._polygon.exterior.coords
        l = len(cs)
        i = randint(0,l-1)
        th = atan2(*cs[i])
        dth = pi * 2/3 * (1 if randint(0,1) == 1 else -1)
        j = min([j for j in range(l) if j != i],
                key=lambda j: abs(th - atan2(*cs[j]) - dth))
        if i > j:
            i, j = j, i

        acs = [c] + [cs[k] for k in range(j, l)] + [cs[k] for k in range(i+1)]
        bcs = [c] + [cs[k] for k in range(i, j+1)]

        u = self._u()
        p = array(self._location)
        va = self._orthogonal(self._project(cs[i], u) + self._project(cs[j], u), p)
        acdir = self._orthogonal(self._project(Polygon(acs).centroid.coords[0], u), p)
        if dot(va, acdir) < 0:
            va = -va
        vb = -va

        return (Shape(acs, self._location, self._orientation, self._velocity + va),
                Shape(bcs, self._location, self._orientation, self._velocity + vb))

    @staticmethod
    def _orthogonal(v, n):
        """Orthogonal projection of a vector in the given plane."""
        return v - n * dot(v, n)

    def _u(self):
        """Unit vector determined by the orientation point."""
        u = cross(self._location, self._orientation)
        return u / norm(u)

    def _project(self, c, u):
        """Project the given coordinate pair onto the sphere using the given
        orientation unit vector.
        """
        # convert to polar coordinates
        x, y = c
        r = sqrt(x*x + y*y)
        th = atan2(y, x)

        # rotate the orientation vector about the location by theta,
        # then rotate the location vector about that by r
        return self._rotate(self._location, self._rotate(u, self._location, th), r)

    def _unproject(self, v, u):
        """Get the local coordinates for a vector on the sphere using the given
        orientation unit vector.
        """
        # r is the angular distance to the location
        r = acos(dot(v, self._location))

        # theta is the angle between the axis of rotation between them
        # and the orientation vector
        vth = self._orthogonal(cross(self._location, v), array(self._location))
        vth = vth/norm(vth)
        th = acos(dot(u, vth))

        # adjust the sign
        if (u[1]*vth[2] - u[2]*vth[1]) * self._location[0] < 0:
            th *= -1

        return r*cos(th), r*sin(th) 

    def projection(self):
        """Project onto the sphere as a spherical polygon and create a new page
        of history.
        """
        self._history.append(dict())
        u = self._u()

        vectors = [self._project(c, u) for c in self._polygon.exterior.coords]
        return SphericalPolygon(self, vectors, self._location)

    def apply_velocity(self, dt):
        """Update by the given timestep."""
        d = norm(self._velocity) * dt

        if d:
            axis = cross(self._location, self._velocity)
            axis = axis / norm(axis)

            self._location, self._orientation, self._velocity = [self._rotate(i, axis, d)
                                                                 for i in
                                                                 self._location,
                                                                 self._orientation,
                                                                 self._velocity]

    def recordvalue(self, v, value):
        """Record the value in the current page of history."""
        self._history[-1][self._unproject(v, self._u())] = value
