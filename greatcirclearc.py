from math import acos, pi

from numpy import dot, cross
from numpy.linalg import norm

from greatcircle import *

class GreatCircleArc(object):
    def __init__(self, start, end):
        self._start = start
        self._end = end

    def range(self):
        vs = [self._start, self._end]
        inflection = GreatCircle(self._start, self._end).inflection()
        if self.contains(inflection):
            vs += [inflection]
        return [[f([v[i] for v in vs]) for i in range (3)]
                for f in min, max]

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
    def _angleaxis(v1, v2):
        return acos(dot(v1, v2)), cross(v1, v2)

    def contains(self, v):
        th, ax = self._angleaxis(self._start, self._end)
        th1, ax1 = self._angleaxis(self._start, v)
        th2, ax2 = self._angleaxis(v, self._end)
        if ax1[0] * ax[0] < 0:
            th1 += pi
        if ax2[0] * ax[0] < 0:
            th2 += pi
        
        return th1 < th and th2 < th
