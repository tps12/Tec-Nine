from pickle import dump, load

from grid import Grid

class Adjacency(object):
    CACHE = '.adj.hex.{0}.pickle'

    def __init__(self, grid):
        cache = self.CACHE.format(grid.size)

        try:
            with open(cache, 'rb') as f:
                self._adj = load(f)
        except Exception as er:
            print('Cached adjacency list failed:', repr(er))

            size = grid.size
            grid = Grid()
            while grid.size != size:
                grid = Grid(grid)
                grid.populate()

            self._adj = {}

            for face in grid.faces:
                self._adj[face] = grid.neighbors(face)

            with open(cache, 'wb') as f:
                dump(self._adj, f, 0)

    def __getitem__(self, v):
        return self._adj[v]
