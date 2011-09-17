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
        self._initrange()
        self._circle = GreatCircle(self._start, self._end)

    @staticmethod
    def _coords(v):
        return tuple([c * 180/pi for c in
            atan2(v[2], sqrt(v[0]*v[0] + v[1]*v[1])), atan2(v[1], v[0])])

    def range(self):
        return self._latrange, self._lonrange

    def _initrange(self):
        s, e = [self._coords(v) for v in self._start, self._end]
        lonrange = LonRange(s[1], e[1])
        latrange = LatRange(s[0], e[0])

        inflection = self._coords(GreatCircle(self._start, self._end).inflection())
        if lonrange.contains(inflection[1]):
            latrange.max = inflection[0]
        if lonrange.contains(inflection[1] - 180):
            latrange.min = -inflection[0]

        self._latrange, self._lonrange = latrange, lonrange

    def __str__(self):
        return ' '.join(['GreatCircleArc:', str(self._start), str(self._end)])

    def intersects(self, other):
        intersections = self._circle.intersects(other._circle)

        for intersection in intersections:
            if self.contains(intersection) and other.contains(intersection):
                return True

        return False

    def contains(self, v):
        return self._lonrange.contains(atan2(v[1],v[0])*180/pi)
