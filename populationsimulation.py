import random
import time

from grid import Grid
from hexadjacency import Adjacency
from planetdata import Data
from populationmethod import eden, expandpopulation
from riversmethod import run
from rock import igneous
from tile import *

class PopulationSimulation(object):
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
            t.climate = None
            t.candidate = False

        self._coastprox = 2
        self._range = 6

        self.adj = Adjacency(self._grid)
        self.initindexes()
        self.populated = set()
        self.popcache = {}

    def initindexes(self):
        self._tileadj = dict()
        for v in self._grid.faces:
            self._tileadj[self.tiles[v]] = set([self.tiles[nv] for nv in self.adj[v]])

    def update(self):
        if not self.populated:
            self.rivers = run(self.tiles.values(), self._tileadj, 5, 0.5)
            self.populated = eden(self.tiles, self._tileadj, 'Eden')
        if not expandpopulation(self.rivers, self._tileadj, self.populated, set(), self.range, self.coastprox, self.popcache):
            return True
        time.sleep(0.1)

    @property
    def grid(self):
        return self._grid

    @property
    def range(self): return self._range

    @range.setter
    def range(self, value):
        self._range = value

    @property
    def coastprox(self): return self._coastprox

    @coastprox.setter
    def coastprox(self, value):
        self._coastprox = value

    @staticmethod
    def seafloor():
        return igneous.extrusive(0.5)

    def load(self, filename):
        data = Data.load(filename)

        random.setstate(data['random'])
        self.tiles = data['tiles']
        self.initindexes()
        self.popcache = {}
