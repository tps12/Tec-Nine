from math import asin, atan2, cos, pi, sin, sqrt

class GreatCircle(object):
    def __init__(self, start, end):
        self._start = start
        self._end = end
        self.plane = self._plane()

    def inflection(self):
        a, b, c = self.plane

        a2b2 = a*a + b*b
        maxz = sqrt(a2b2/(a2b2 + c*c))

        return (-a*c*maxz/a2b2,
                (-c*maxz + (a*a*c*maxz)/a2b2)/b,
                maxz)

    def intersects(self, other):
        if self.plane == (0,0,0) or other.plane == (0,0,0):
            return []

        sa, sb, sc = self.plane
        oa, ob, oc = other.plane

        num = oa * sc - oc * sa
        den = ob * sa - oa * sb
        g = num/den

        num = -g * sb - sc
        h = num / sa

        den = h*h + g*g + 1
        w = sqrt(1/den)

        return (h*w, g*w, w), (-h*w, -g*w, -w)

    def _plane(self):
        vs = self._start, self._end
        return (vs[0][1] * vs[1][2] - vs[1][1] * vs[0][2],
                vs[1][0] * vs[0][2] - vs[0][0] * vs[1][2],
                vs[0][0] * vs[1][1] - vs[1][0] * vs[0][1])
