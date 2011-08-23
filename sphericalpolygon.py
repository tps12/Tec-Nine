from greatcirclearc import *

class SphericalPolygon(object):
    def __init__(self, points):
        self._points = [p for p in points]
        self.latrange, self.lonrange = self._getranges(self._points)
        self._externalpoint = self._guessexternal(self.latrange, self.lonrange)

    @staticmethod
    def _getranges(points):
        lonrange = GreatCircleArc(points[0], points[1]).lonrange
        latrange = LatRange(points[0][0], points[1][0])

        for i in range(1, len(points)-1):
            arc = GreatCircleArc(points[i], points[i+1])
            if not latrange.meld(arc.latrange):
                raise Exception(' '.join(["Can't meld", str(arc.latrange),
                                          'into', str(latrange)]))
            if not lonrange.meld(arc.lonrange):
                raise Exception(' '.join(["Can't meld", str(arc.lonrange),
                                          'into', str(lonrange)]))
        return latrange, lonrange

    @staticmethod
    def _guessexternal(latrange, lonrange):
        if lonrange.max - lonrange.min >= 360:
            externallon = 90.0
            if latrange.max < 0:
                externallat = 45.0
            elif latrange.min > 0:
                externallat = -45.0
            elif abs(latrange.max) > abs(latrange.min):
                externallat = latrange.min - (90 + latrange.min)/2.0
            else:
                externallat = latrange.max + (90 - latrange.max)/2.0
        else:
            externallon = (lonrange.max + lonrange.min)/2.0 - 180
            while externallon < -180: externallon += 360
            while externallon > 180: externallon -= 360

            if abs(latrange.max) >= abs(latrange.min):
                externallat = latrange.min + (-90 - latrange.min)/2.0
            else:
                externallat = latrange.max + (90 - latrange.max)/2.0

        return externallat, externallon

    def contains(self, point):
        count = 0
        arc = GreatCircleArc(point, self._externalpoint)

        for i in range(len(self._points)-1):
            if arc.intersects(GreatCircleArc(self._points[i],
                                             self._points[i+1])):
                count += 1
        return (count % 2) == 1
