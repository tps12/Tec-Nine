import random
import time

from grid import Grid
from hexadjacency import Adjacency
from planetdata import Data
from riversmethod import run
from rock import igneous
from tile import *

class RiversSimulation(object):
    def __init__(self):
        grid = Grid()
        while grid.size < 6:
            grid = Grid(grid)
            grid.populate()
        self._grid = grid

        self.tiles = {}
        for v in self._grid.faces:
            x, y, z = v
            lat = 180/pi * atan2(z, sqrt(x*x + y*y))
            lon = 180/pi * atan2(y, x)
            self.tiles[v] = Tile(lat, lon)

        for t in self.tiles.itervalues():
            t.emptyocean(self.seafloor())
            t.climate = t.seasons = None
            t.candidate = False

        self._hmin = 5
        self._pmin = 0.5

        self.adj = Adjacency(self._grid)
        self.initindexes()
        self.rivers = []

    def initindexes(self):
        self._tileadj = dict()
        for v in self._grid.faces:
            self._tileadj[self.tiles[v]] = set([self.tiles[nv] for nv in self.adj[v]])

    def update(self):
       self.rivers = run(self.tiles.values(), self._tileadj, self._hmin, self._pmin)

    @property
    def grid(self):
        return self._grid

    @property
    def hmin(self): return self._hmin

    @hmin.setter
    def hmin(self, value):
        self._hmin = value
        self.update()

    @property
    def pmin(self): return self._pmin

    @pmin.setter
    def pmin(self, value):
        self._pmin = value
        self.update()

    @staticmethod
    def seafloor():
        return igneous.extrusive(0.5)

    def load(self, filename):
        data = Data.load(filename)

        random.setstate(data['random'])
        self.tiles = data['tiles']
        self.initindexes()
        self.update()
