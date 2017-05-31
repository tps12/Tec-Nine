import math
import random
import time

from climatemethod import climate
from grid import Grid
from hexadjacency import Adjacency
from planetdata import Data
from populationmethod import eden, expandpopulation, habitable
from racinatemethod import racinate
from riversmethod import run
from rock import igneous
from tile import *
from timing import Timing

def agprob(k):
  if k[0] == u'B':
    return 0.05
  if k[0] == u'C':
    return 0.005
  if k[0] == u'D':
    return 0.001
  if k == u'Aw':
    return 0.0001
  return 0

class PrehistorySimulation(object):
    coastprox = 2
    range = 6
    seasons = [-1, -0.5, 0, 0.5, 1, 0.5, 0, -0.5]
    cells = 3
    spin = 1.0
    tilt = 23
    mean_temprange = (-25.0, 50.0)
    glaciationstep = 16
    anthroglacial = 6

    def __init__(self):
        self._timing = Timing()

        initt = self._timing.routine('simulation setup')

        initt.start('building grid')

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

        initt.start('building indexes')
        self.shapes = []
        self.adj = Adjacency(self._grid)
        self._glaciationt = 0
        self.initindexes()
        self.populated = {}
        self.agricultural = set()

        initt.done()

    def initindexes(self):
        self._tileadj = dict()
        for v in self._grid.faces:
            self._tileadj[self.tiles[v]] = set([self.tiles[nv] for nv in self.adj[v]])

    def update(self):
        stept = self._timing.routine('simulation step')

        stept.start('identifying glaciers')
        gs = [sum([1 for t in s.tiles if t.climate and t.climate.koeppen[0] == u'E']) for s in self.shapes]

        stept.start('iterating climate')
        glaciation = 0.5 - math.cos(self._glaciationt*math.pi/self.glaciationstep)/2
        dtemp = 5 * (glaciation / 0.5)
        temprange = (self.mean_temprange[0] + dtemp, self.mean_temprange[1] + dtemp)
        c = climate(self.tiles, self.adj, self.seasons, self.cells, self.spin, self.tilt, temprange, glaciation, True, {})
        for v, tile in self.tiles.iteritems():
            tile.climate = c[v]['classification']
            if not habitable(tile) and tile in self.populated:
                del self.populated[tile]

        stept.start('applying isostasy')
        for s, g in zip(self.shapes, gs):
            dg = sum([1 for t in s.tiles if t.climate and t.climate.koeppen[0] == u'E']) - g
            dh = 0.6 * dg / len(s.tiles)
            for t in s.tiles:
                t.isostasize(dh)

        self._glaciationt += 1

        if not self.populated:
            stept.start('genesis')
            self.populated = eden(self.tiles, self._tileadj)

        stept.start('running rivers')
        rivers = run(self.tiles.values(), self._tileadj, 5, 0.5)

        stept.start('sparking agriculture')
        for r in rivers:
            for t in r:
                if t in self.populated and t not in self.agricultural and random.random() < agprob(t.climate.koeppen):
                    self.agricultural.add(self.populated[t])

        popcache = {}
        for i in range(self.anthroglacial):
            stept.start('migration {}'.format(i))
            if not expandpopulation(rivers, self._tileadj, self.populated, self.agricultural, self.range, self.coastprox, popcache):
                break
        stept.start('identifying distinct populations')
        racinate(self.tiles.values(), self._tileadj, self.populated, self.agricultural, self.range)

        stept.done()

    @property
    def grid(self):
        return self._grid

    @property
    def peoples(self):
        return len({p for p in self.populated.itervalues()})

    @staticmethod
    def seafloor():
        return igneous.extrusive(0.5)

    def loaddata(self, data):
        random.setstate(data['random'])
        self.tiles = data['tiles']
        self.shapes = data['shapes']
        self.populated = data['population']
        self.agricultural = data['agricultural']
        self._glaciationt = data['glaciationtime']
        self.initindexes()

    def load(self, filename):
        self.loaddata(Data.load(filename))

    def savedata(self):
        return Data.savedata(random.getstate(), 0, None, None, None, self.tiles, self.shapes, self._glaciationt, self.populated, self.agricultural, True, True)

    def save(self, filename):
        Data.save(filename, self.savedata())
