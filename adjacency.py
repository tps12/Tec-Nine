from cPickle import dump, load
from math import pi, sqrt

class Adjacency(object):
    CACHE = '.adj.{0}.pickle'

    def __init__(self, tiles):
        cache = self.CACHE.format(len(tiles))

        try:
            with open(cache, 'r') as f:
                self._adj = load(f)
        except Exception as er:
            print 'Cached adjacency list failed:', repr(er)
            self._adj = {}

            def addadj(t1, t2):
                if t1 in self._adj:
                    adj = self._adj[t1]
                else:
                    adj = []
                    self._adj[t1] = adj
                adj.append(t2)

            def addadjes(t1, t2):
                addadj(t1, t2)
                addadj(t2, t1)

            limit = sqrt(2) * pi / len(tiles)
            
            for i in range(1, len(tiles)):
                for j in range(len(tiles[i])):
                    t1 = tiles[i][j]
                    for k in range(len(tiles[i-1])):
                        if t1.distance(tiles[i-1][k]) <= limit:
                            addadjes((j,i),(k,i-1))
                    addadj((j,i),(j-1 if j > 0 else len(tiles[i])-1, i))
                    addadj((j,i),(j+1 if j < len(tiles[i])-1 else 0, i))

            with open(cache, 'w') as f:
                dump(self._adj, f, 0)

    def __getitem__(self, coords):
        return self._adj[coords]
