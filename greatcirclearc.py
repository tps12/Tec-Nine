from math import acos, atan2, pi, sqrt

from numpy import dot, cross
from numpy.linalg import norm

from greatcircle import *
from lonrange import *
from latrange import *

class GreatCircleArc(object):
    def __init__(self, start, end):
        self._start = start
        self._end = end

    @staticmethod
    def _coords(v):
        return tuple([c * 180/pi for c in
            atan2(v[2], sqrt(v[0]*v[0] + v[1]*v[1])), atan2(v[1], v[0])])

    def range(self):
        s, e = [self._coords(v) for v in self._start, self._end]
        lonrange = LonRange(s[1], e[1])
        latrange = LatRange(s[0], e[0])

        inflection = self._coords(GreatCircle(self._start, self._end).inflection())
        if lonrange.contains(inflection[1]):
            latrange.max = inflection[0]
        if lonrange.contains(inflection[1] - 180):
            latrange.min = -inflection[0]

        return latrange, lonrange

    def __str__(self):
        return ' '.join(['GreatCircleArc:', str(self._start), str(self._end)])

    def intersects(self, other):
        intersections = GreatCircle(self._start, self._end).intersects(
            GreatCircle(other._start, other._end))

        for intersection in intersections:
            if self.contains(intersection) and other.contains(intersection):
                return True

        return False

    @staticmethod
    def _anglea(v1, v2):
        return acos(dot(v1, v2)), v1[1]*v2[2] - v1[2]*v2[1]

    def contains(self, v):
        th, a = self._anglea(self._start, self._end)
        th1, a1 = self._anglea(self._start, v)
        th2, a2 = self._anglea(v, self._end)
        if a1 * a < 0:
            th1 += pi
        if a2 * a < 0:
            th2 += pi
        
        return th1 < th and th2 < th
