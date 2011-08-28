from greatcircle import *

class GreatCircleArc(object):
    def __init__(self, start, end):
        self._start = start
        self._end = end

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
        es = self._start, self._end
        h2 = sum([(es[1][i] - es[0][i])**2 for i in range(3)])
        return all([sum([(v[i] - e[i])**2 for i in range(3)]) < h2 for e in es])
