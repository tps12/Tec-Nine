import math
import random
import time

from climatemethod import climate
from grid import Grid
from hexadjacency import Adjacency
from planetdata import Data
from populationmethod import eden, expandpopulation, habitable, sea
from racinatemethod import racinate
from rock import igneous
from tile import *

class PrehistorySimulation(object):
    coastprox = 2
    range = 6
    seasons = [-1, -0.5, 0, 0.5, 1, 0.5, 0, -0.5]
    cells = 3
    spin = 1.0
    tilt = 23
    mean_temprange = (-25.0, 50.0)
    glaciationstep = 16
    anthroglacial = 2

    def __init__(self):
        grid = Grid()
        while grid.size < 6:
            grid = Grid(grid)
            grid.populate()
        self._grid = grid

        self.tiles = {}
        for v in self._grid.faces:
            x, y, z = v
            lat = 180/pi * atan2(y, sqrt(x*x + z*z))
            lon = 180/pi * atan2(-x, z)
            self.tiles[v] = Tile(lat, lon)

        for t in self.tiles.itervalues():
            t.emptyocean(self.seafloor())
            t.climate = None
            t.candidate = False

        self.adj = Adjacency(self._grid)
        self._glaciationt = 0
        self.initindexes()
        self.populated = {}

    def initindexes(self):
        self._tileadj = dict()
        for v in self._grid.faces:
            self._tileadj[self.tiles[v]] = set([self.tiles[nv] for nv in self.adj[v]])

    def update(self):
        glaciation = 0.5 - math.cos(self._glaciationt*math.pi/self.glaciationstep)/2
        dtemp = 5 * (glaciation / 0.5)
        temprange = (self.mean_temprange[0] + dtemp, self.mean_temprange[1] + dtemp)
        c = climate(self.tiles, self.adj, self.seasons, self.cells, self.spin, self.tilt, temprange, glaciation, True, {})
        for v, tile in self.tiles.iteritems():
            tile.climate = c[v]['classification']
            if not habitable(tile) and tile in self.populated:
                del self.populated[tile]
        self._glaciationt += 1

        if not self.populated:
            self.sea = sea(self.tiles)
            self.populated = eden(self.tiles, self.sea, self._tileadj)

        for _ in range(self.anthroglacial):
            expandpopulation(self.sea, self._tileadj, self.populated, self.range, self.coastprox)
        racinate(self.tiles.values(), self._tileadj, self.populated, self.range)

    @property
    def grid(self):
        return self._grid

    @property
    def peoples(self):
        return len({p for p in self.populated.itervalues()})

    @staticmethod
    def seafloor():
        return igneous.extrusive(0.5)

    def load(self, filename):
        data = Data.load(filename)

        random.setstate(data['random'])
        self.tiles = data['tiles']
        self._glaciationt = random.randint(0,self.glaciationstep-1)
        self.initindexes()
