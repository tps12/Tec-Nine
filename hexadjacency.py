from cPickle import dump, load

class Adjacency(object):
    CACHE = '.adj.hex.{0}.pickle'

    def __init__(self, grid):
        cache = self.CACHE.format(grid.size)

        try:
            with open(cache, 'r') as f:
                self._adj = load(f)
        except Exception as er:
            print 'Cached adjacency list failed:', repr(er)
            self._adj = {}

            for face in grid.faces:
                self._adj[face] = grid.neighbors(face)

            with open(cache, 'w') as f:
                dump(self._adj, f, 0)

    def __getitem__(self, v):
        return self._adj[v]
