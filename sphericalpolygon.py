from numpy import *
from numpy.linalg import *

from greatcirclearc import *

class SphericalPolygon(object):
    def __init__(self, vectors):
        self._vectors = [v for v in vectors]
        self._externalvector = self._guessexternal(self._vectors)
        for v in self._vectors:
            print v
        print '--'
        print self._externalvector

    @staticmethod
    def _guessexternal(vs):
        s = [0,0,0]
        for v in vs:
            for i in range(3):
                s[i] += v[i]
        e = array([-s[i]/len(vs) for i in range(3)])
        return e/norm(e)

    def contains(self, vector):
        count = 0
        arc = GreatCircleArc(vector, self._externalvector)

        for i in range(-1, len(self._vectors)-1):
            if arc.intersects(GreatCircleArc(self._vectors[i],
                                             self._vectors[i+1])):
                count += 1
        return (count % 2) == 1
