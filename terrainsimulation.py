import math
import random
import time

from dist2 import dist2
from grid import Grid
from hexadjacency import Adjacency
from planetdata import Data
from pointtree import PointTree
from prehistorysimulation import PrehistorySimulation
import riversmethod
from rock import igneous
from terrainmethod import terrain, elevation, routerivers
from tile import *
from timing import Timing

class TerrainSimulation(object):
    _timing = Timing()
    minriverelev = PrehistorySimulation.minriverelev
    minriverprecip = PrehistorySimulation.minriverprecip

    def __init__(self, gridsize):
        initt = self._timing.routine('simulation setup')

        initt.start('building grid')

        self._initgrid(gridsize)

        self.tiles = {}
        for v in self._grid.faces:
            x, y, z = v
            lat = 180/pi * atan2(z, sqrt(x*x + y*y))
            lon = 180/pi * atan2(y, x)
            self.tiles[v] = Tile(lat, lon)
        self._tileloc = {t: f for f,t in self.tiles.items()}

        for t in self.tiles.values():
            t.emptyocean(self.seafloor())
            t.climate = t.seasons = None
            t.candidate = False

        self._terrain = terrain(self.grid, self.tiles)
        self.terrainchanged = False

        initt.start('building indexes')
        self.shapes = []
        self.adj = Adjacency(self._grid)
        self._glaciationt = 0
        self.initindexes()
        self.populated = {}
        self.agricultural = set()
        self.rivers = []
        self.riverroutes = []

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

    @property
    def faces(self):
        faces = {}
        grid = self._terrain
        while True:
            for f, vs in grid.faces.items():
                if f not in faces:
                    faces[f] = vs
            if grid == self._grid:
               break
            grid = grid.prev
        return faces

    @staticmethod
    def seafloor():
        return igneous.extrusive(0.5)

    def faceelevation(self, f):
        return elevation(f, self._terrain, self.tiles)

    def riverface(self, f):
        return any([f in r for r in self.riverroutes])

    def loaddata(self, data, loadt):
        random.setstate(data['random'])
        loadt.start('initializing grid')
        self._initgrid(data['gridsize'])
        self.spin, self.cells, self.tilt = [data[k] for k in ['spin', 'cells', 'tilt']]
        self.tiles = data['tiles']
        self._tileloc = {t: f for f,t in self.tiles.items()}
        loadt.start('subdividing tiles')
        self._terrain = terrain(self.grid, self.tiles)
        self._terrainadj = Adjacency(self._terrain)
        self.terrainchanged = True
        self.shapes = data['shapes']
        self.populated = data['population']
        self.agricultural = data['agricultural']
        self._glaciationt = data['glaciationtime']
        loadt.start('initializing indexes')
        self.initindexes()
        loadt.start('running rivers')
        self.rivers = riversmethod.run(self.tiles.values(), self._tileadj, self.minriverelev, self.minriverprecip)
        self.riverroutes = list(routerivers(
            self._terrain, self._terrainadj, {f: self.faceelevation(f) for f in self._terrain.faces},
            [[self._tileloc[t] for t in r] for r in self.rivers]))

    def load(self, filename):
        loadt = self._timing.routine('loading state')
        loadt.start('reading file')
        self.loaddata(Data.load(filename), loadt)
        loadt.done()

    def savedata(self):
        return Data.savedata(random.getstate(), self._grid.size, 0, self.spin, self.cells, self.tilt, None, None, None, self.tiles, self.shapes, self._glaciationt, self.populated, self.agricultural, True, True, [], {}, {}, [], {}, {}, {}, [])

    def save(self, filename):
        Data.save(filename, self.savedata())
