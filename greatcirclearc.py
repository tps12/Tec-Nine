from latrange import *
from lonrange import *
from greatcircle import *

class GreatCircleArc(object):
    def __init__(self, start, end):
        self._start = start
        self._end = end

        self.meridian = (self._start[1] == self._end[1] or
                         self._start[1] == self._end[1] + 180 or
                         self._start[1] == self._end[1] - 180)

        if not self.meridian:
            self._start, self._end = self._orient(self._start, self._end)

        self.lonrange = LonRange(self._start[1], self._end[1])
        self.latrange = LatRange(self._start[0], self._end[0])

        inflection = GreatCircle(self._start, self._end).inflection()

        if not self.meridian and self.lonrange.contains(inflection[1]):
            self.latrange.max = inflection[0]

        if not self.meridian and self.lonrange.contains(inflection[1] - 180):
            self.latrange.min = -inflection[0]

    @staticmethod
    def _normalize(p):        
        while p[1] < -180: p = p[0], p[1]+360
        while p[1] > 180:  p = p[0], p[1]-360
        return p

    @staticmethod
    def _orient(a, b):
        a, b = [GreatCircleArc._normalize(p) for p in a,b]

        while a[1] < 0 or b[1] < 0:
            a = a[0], a[1]+360
            b = b[0], b[1]+360

        if a[1] < b[1] and b[1] - a[1] > 180:
            last = a
            a = b
            b = last

        if a[1] > b[1] and a[1] - b[1] > 180:
            b = b[0], b[1]+360

        if a[1] > b[1] and a[1] - b[1] < 180:
            last = a
            a = b
            b = last

        return [GreatCircleArc._normalize(p) for p in a,b]

    def __str__(self):
        return ' '.join(['GreatCircleArc:', str(self._start), str(self._end)])

    def intersects(self, other):
        if not self.lonrange.overlaps(other.lonrange):
            return False
        if not self.latrange.overlaps(other.latrange):
            return False

        if self.meridian and other.meridian:
            if ((self._start[1] == self._end[1] + 180 or
                 self._start[1] + 180 == self._end[1]) and
                (other._start[1] == other._end[1] + 180 or
                 other._start[1] + 180 == self._end[1])):
                return ((self._start[0] >= 0 and other._start[0] >= 0) or
                        (self._start[1] <= 0 and other._start[1] <= 0))
            else:
                return False

        intersections = GreatCircle(self._start, self._end).intersects(
            GreatCircle(other._start, other._end))

        def meridian_intersects(arc, intersection):
            return (arc.meridian and            
                    min(arc._start[0], arc._end[0]) <= intersection[0] and
                    max(arc._start[0], arc._end[0]) >= intersection[0])

        for arc in [self, other]:
            for intersection in intersections:
                if meridian_intersects(arc, intersection):
                    return True

        if self.meridian or other.meridian:
            return False

        for intersection in intersections:
            if (self.lonrange.contains(intersection[1]) and
                other.lonrange.contains(intersection[1])):
                return True

        return False
