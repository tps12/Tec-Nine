from numpy import array
from numpy.linalg import norm

from greatcirclearc import *

class SphericalPolygon(object):
    def __init__(self, vectors):
        self._vectors = [v for v in vectors]
        self._arcs = [self._getarc(self._vectors[i], self._vectors[i+1])
                      for i in range(-1, len(self._vectors)-1)]
        self._externalvector = self._guessexternal(self._vectors)

    @staticmethod
    def _getarc(v1, v2):
        vs = (v2, v1) if v1[0]*v2[1] - v1[1]*v2[0] < 0 else (v1,v2)
        return GreatCircleArc(*vs)

    @staticmethod
    def _guessexternal(vs):
        s = [0,0,0]
        for v in vs:
            for i in range(3):
                s[i] += v[i]
        e = array([-s[i]/len(vs) for i in range(3)])
        return e/norm(e)

    def _eacharc(self, f):
        for arc in self._arcs:
            yield f(arc)

    def contains(self, vector):
        count = 0
        arc = GreatCircleArc(vector, self._externalvector)

        count = len([isects for isects in self._eacharc(lambda a: arc.intersects(a)) if isects])

        return (count % 2) == 1
