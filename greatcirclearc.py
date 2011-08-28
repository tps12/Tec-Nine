from math import acos

from numpy import dot

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

    def contains(self, v):
        th = acos(dot(self._start, self._end))
        return (acos(dot(self._start, v)) <= th and
                acos(dot(v, self._end)) <= th)
