from numpy import *
from numpy.linalg import *

from greatcirclearc import *

class SphericalPolygon(object):
    def __init__(self, vectors):
        self._vectors = [v for v in vectors]
        self._externalvector = self._guessexternal(self._vectors)

    @staticmethod
    def _guessexternal(vs):
        s = [0,0,0]
        for v in vs:
            for i in range(3):
                s[i] += v[i]
        e = array([-s[i]/len(vs) for i in range(3)])
        return e/norm(e)

    def _eacharc(self, f):
        for i in range(-1, len(self._vectors)-1):
            yield f(GreatCircleArc(self._vectors[i], self._vectors[i+1]))

    def range(self):
        def meld(a, b):
            return ([min(a[0][i], b[0][i]) for i in range(3)],
                    [max(a[1][i], b[1][i]) for i in range(3)])

        return reduce(meld, self._eacharc(lambda a: a.range()))

    def contains(self, vector):
        count = 0
        arc = GreatCircleArc(vector, self._externalvector)

        count = len([isects for isects in self._eacharc(lambda a: arc.intersects(a)) if isects])

        return (count % 2) == 1
