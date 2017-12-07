from math import pi
import random

from climatemethod import climate, temprange
from grid import Grid
from hexadjacency import *
import lifeformsmethod
from planetdata import Data
from pointtree import PointTree
from rock import igneous
import species
from tile import *
from timing import Timing

class LifeformsSimulation(object):
    mean_temprange = (-25.0, 50.0)
    seasons = [-1, -0.5, 0, 0.5, 1, 0.5, 0, -0.5]

    def __init__(self, gridsize):
        self._timing = Timing()

        initt = self._timing.routine('simulation setup')

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

        initt.start('building indexes')
        self.shapes = []
        self.adj = Adjacency(self._grid)
        self._glaciationt = 0
        self.initindexes()
        self.populated = {}
        self.agricultural = set()
        self.fauna = []
        self.plants = []
        self.trees = []
        self._species = None

        initt.done()

    def _initgrid(self, gridsize):
        grid = Grid()
        while grid.size < gridsize:
            grid = Grid(grid)
            grid.populate()
        self._grid = grid

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

    @property
    def grid(self):
        return self._grid

    def classify(self):
        c = climate(self.tiles, self.adj, self.seasons, self.cells, self.spin, self.tilt, temprange(self.mean_temprange, self.glaciation), self.glaciation, True, {})
        for v, tile in self.tiles.items():
            tile.climate = c[v]['classification']
            tile.seasons = c[v]['seasons']

    def settle(self):
        timing = self._timing.routine('settling species')
        timing.start('classifying climate')
        self.classify()

        lifeformsmethod.settle(self.fauna, self.plants, self.trees, self.tiles, self.adj, timing)

        self._species = None
        timing.done()

    def species(self):
        if not self._species:
            timing = self._timing.routine('indexing species')
            types = self.fauna, self.plants, self.trees
            pops = [{} for _ in types]
            for t in range(len(types)):
                p = pops[t]
                for s in types[t]:
                    for f, ss in s.seasonalrange(len(self.seasons)).items():
                        for i in ss:
                            if f not in p:
                                p[f] = [set() for _ in self.seasons]
                            p[f][i].add(s)
            self._species = pops
            timing.done()
        return self._species

    @property
    def glaciation(self):
        return self._glaciation if hasattr(self, '_glaciation') else 0.5

    @glaciation.setter
    def glaciation(self, value):
        self._glaciation = value
        self.settle()

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
        self.settle()

    def load(self, filename):
        self.loaddata(Data.load(filename))

    def savedata(self):
        return Data.savedata(random.getstate(), self._grid.size, 0, self.spin, self.cells, self.tilt, None, None, None, self.tiles, self.shapes, self._glaciationt, self.populated, self.agricultural, True, True, [], {}, {}, [], {}, {}, [])

    def save(self, filename):
        Data.save(filename, self.savedata())
