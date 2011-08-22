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

        self.lonrange = LonRange(self._start[1], self._end[1])
        self.latrange = LatRange(self._start[0], self._end[0])

        inflection = GreatCircle(self._start, self._end).inflection()

        if not self.meridian and self.lonrange.contains(inflection[1]):
            self.latrange.max = inflection[0]

        if not self.meridian and self.lonrange.contains(inflection[1] - 180):
            self.latrange.min = -inflection[0]
       

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

        intersections = GreatCircle(self._start, self._end).intersect(
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
                other.lonrange.contains(intersectian[1])):
                return True

        return False
