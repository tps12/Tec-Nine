from math import asin, atan2, cos, pi, sin, sqrt

class GreatCircle(object):
    def __init__(self, start, end):
        self._start = start
        self._end = end

        self.meridian = (self._start[1] == self._end[1] or
                         self._start[1] == self._end[1] + 180 or
                         self._start[1] == self._end[1] - 180)

    
    def inflection(self):
        if self._start[0] == self._end[0] and self._start[1] == self._end[1]:
            return [c for c in self._start]

        a, b, c = self.plane()
        a2b2 = a*a + b*b
        maxz = sqrt(a2b2/(a2b2 + c*c))

        x,y,z = (-a*c*maxz/a2b2,
                 (-c*maxz + (a*a*c*maxz)/a2b2)/b,
                 maxz)

        return self.point(x,y,z)

    def intersects(self, other):
        if self.meridian and other.meridian:
            return (90.0, 135.0), (-90.0, -135.0)

        if self.meridian or other.meridian:
            raise Exception("Don't know how to intersect meridian with non-meridian.")

        sa, sb, sc = self.plane()
        oa, ob, oc = other.plane()

        num = oa * sc - oc * sa
        den = ob * sa - oa * sb
        g = num/den

        num = -g * sb - sc
        h = num / sa

        den = pow(h, 2) + pow(g, 2) + 1
        w = sqrt(1/den)

        return [self.point(*v) for v in
                (h*w, g*w, w), (-h*w, -g*w, w)]

    @staticmethod
    def point(x, y, z):
        lat = asin(z)
        lon = atan2(y, x)
        return [a * 180/pi for a in lat, lon]

    @staticmethod
    def vector(lat, lon):
        lat, lon = [a * pi/180 for a in lat, lon]
        clat = cos(lat)
        return cos(lon) * clat, sin(lon) * clat, sin(lat)

    def plane(self):
        vs = [self.vector(*p) for p in self._start, self._end]
        return (vs[0][1] * vs[1][2] - vs[1][1] * vs[0][2],
                vs[1][0] * vs[0][2] - vs[0][0] * vs[1][2],
                vs[0][0] * vs[1][1] - vs[1][0] * vs[0][1])
