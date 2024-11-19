import math
import random
import time

from climatemethod import climate, temprange
from grid import Grid
from hexadjacency import Adjacency
from language import output
from language.lexicon import lexicon
from language.phonemes import phonemes
from planetdata import Data
from pointtree import PointTree
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
    mean_temprange = (-25.0, 50.0)
    minriverelev = 5
    minriverprecip = 0.5
    glaciationstep = 16
    anthroglacial = 6

    def __init__(self):
        self._timing = Timing()

    def create(self, gridsize, spin, cells, tilt):
        self._timing = Timing()

        initt = self._timing.routine('simulation setup')

        self.spin, self.cells, self.tilt = spin, cells, tilt

        initt.start('building grid')

        self._initgrid(gridsize)

        self.tiles = {}
        for v in self._grid.faces:
            x, y, z = v
            lat = 180/pi * atan2(z, sqrt(x*x + y*y))
            lon = 180/pi * atan2(y, x)
            self.tiles[v] = Tile(lat, lon)

        for t in self.tiles.values():
            t.emptyocean(self.seafloor())
            t.climate = t.seasons = None
            t.candidate = False

        initt.start('building indexes')
        self.shapes = []
        self._glaciationt = 0
        self.initindexes()
        self.populated = {}
        self.agricultural = set()

        initt.done()
        return self

    def _initgrid(self, gridsize):
        grid = Grid()
        while grid.size < gridsize:
            grid = Grid(grid)
            grid.populate()
        self._grid = grid
        self.adj = Adjacency(self._grid)

    def initindexes(self):
        self._indexedtiles = []
        for t in self.tiles.values():
            self._indexedtiles.append(t)

        self._tileadj = dict()
        for v in self._grid.faces:
            self._tileadj[self.tiles[v]] = set([self.tiles[nv] for nv in self.adj[v]])

        self._index = PointTree(dict([[self._indexedtiles[i].vector, i]
                                      for i in range(len(self._indexedtiles))]))

    def nearest(self, loc):
        return self._indexedtiles[self._index.nearest(loc)[0]]

    def newrace(self):
        # TODO make unique
        vs, cs = phonemes()
        name = output.write(random.choice(list(lexicon(vs, cs, round(random.gauss(-0.5, 1)), 0.5, 0.5, None, 1000))))
        return name[0].upper() + name[1:]

    def update(self):
        stept = self._timing.routine('simulation step')

        stept.start('identifying glaciers')
        gs = [sum([1 for t in s.tiles if t.climate and t.climate.koeppen[0] == u'E']) for s in self.shapes]

        stept.start('iterating climate')
        glaciation = 0.5 - math.cos(self._glaciationt*math.pi/self.glaciationstep)/2
        c = climate(self.tiles, self.adj, self.seasons, self.cells, self.spin, self.tilt, temprange(self.mean_temprange, glaciation), glaciation, True, {})
        for v, tile in self.tiles.items():
            tile.climate = c[v]['classification']
            tile.seasons = c[v]['seasons']
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
            self.populated = eden(self.tiles, self._tileadj, self.newrace())

        stept.start('running rivers')
        rivers = run(self.tiles.values(), self._tileadj, self.minriverelev, self.minriverprecip)

        stept.start('sparking agriculture')
        gfactor = math.pow(glaciation, 2)  # Agriculture more likely in interglacial period
        for r in rivers:
            for t in r:
                if t in self.populated and t not in self.agricultural and random.random() < gfactor * agprob(t.climate.koeppen):
                    self.agricultural.add(self.populated[t])

        popcache = {}
        for i in range(self.anthroglacial):
            stept.start('migration {}'.format(i))
            if not expandpopulation(rivers, self._tileadj, self.populated, self.agricultural, self.range, self.coastprox, popcache):
                break
        stept.start('identifying distinct populations')
        racinate(self.tiles.values(), self._tileadj, self.populated, self.newrace, self.agricultural, self.range)

        stept.done()

    @property
    def grid(self):
        return self._grid

    @property
    def peoples(self):
        return len({p for p in self.populated.values()})

    @staticmethod
    def seafloor():
        return igneous.extrusive(0.5)

    def loaddata(self, data):
        random.setstate(data['random'])
        self._initgrid(data['gridsize'])
        self.spin, self.cells, self.tilt = [data[k] for k in ['spin', 'cells', 'tilt']]
        self.tiles = data['tiles']
        self.shapes = data['shapes']
        self.populated = data['population']
        self.agricultural = data['agricultural']
        self._glaciationt = data['glaciationtime']
        self.initindexes()

    def load(self, filename):
        self.loaddata(Data.load(filename))

    def savedata(self):
        return Data.savedata(random.getstate(), self._grid.size, 0, self.spin, self.cells, self.tilt, None, None, None, None, None, self.tiles, self.shapes, self._glaciationt, self.populated, self.agricultural, True, True, False, [], {}, {}, [], {}, {}, [], [])

    def save(self, filename):
        Data.save(filename, self.savedata())
