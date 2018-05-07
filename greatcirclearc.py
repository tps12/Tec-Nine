from math import acos, atan2, pi, sqrt

from numpy import dot, cross
from numpy.linalg import norm

from greatcircle import *

class GreatCircleArc(object):
    def __init__(self, start, end):
        self._start = start
        self._end = end
        self._length = acos(dot(self._start, self._end))
        self._circle = GreatCircle(self._start, self._end)

    @staticmethod
    def _coords(v):
        return tuple([c * 180/pi for c in
                      (atan2(v[2], sqrt(v[0]*v[0] + v[1]*v[1])), atan2(v[1], v[0]))])

    def __str__(self):
        return ' '.join(['GreatCircleArc:', str(self._start), str(self._end)])

    def intersects(self, other):
        intersections = self._circle.intersects(other._circle)

        for intersection in intersections:
            if self.contains(intersection) and other.contains(intersection):
                return True

        return False

    def contains(self, v):
        # add pi to distance if it's on the other side
        dth = pi if dot(cross(self._start, v), self._circle.plane) < 0 else 0
        return acos(dot(v, self._start)) + dth < self._length
