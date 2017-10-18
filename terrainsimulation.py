import math
import random
import time

from grid import Grid
from hexadjacency import Adjacency
from planetdata import Data
from pointtree import PointTree
from rock import igneous
from tile import *
from timing import Timing

class TerrainSimulation(object):
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

        for t in self.tiles.itervalues():
            t.emptyocean(self.seafloor())
            t.climate = None
            t.candidate = False

        self._terrain = self.terrain(self.grid, self.tiles)

        initt.start('building indexes')
        self.shapes = []
        self.adj = Adjacency(self._grid)
        self._glaciationt = 0
        self.initindexes()
        self.populated = {}
        self.agricultural = set()

        initt.done()

    def _initgrid(self, gridsize):
        grid = Grid()
        while grid.size < gridsize:
            grid = Grid(grid)
            grid.populate()
        self._grid = grid

    def initindexes(self):
        self._indexedtiles = []
        for t in self.tiles.itervalues():
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
            for f, vs in grid.faces.iteritems():
                if f not in faces:
                    faces[f] = vs
            if grid == self._grid:
               break
            grid = grid.prev
        return faces

    @staticmethod
    def seafloor():
        return igneous.extrusive(0.5)

    @staticmethod
    def terrain(grid, tiles):
        terrain = Grid(Grid(grid))
        for v, t in tiles.iteritems():
            if t.elevation > 0:
                terrain.populate(v)
        return terrain

    @classmethod
    def components(cls, f, grid, tiles):
        if f in tiles:
            # face has a tile, just return it
            return [[tiles[f]]]
        if f in grid.vertices:
            # average adjacent faces
            return [sum([cls.components(vf, grid, tiles)
                         for vf in grid.vertices[f]], [])]
        # otherwise check in parent
        return [cls.components(f, grid.prev, tiles)]

    def facecomponents(self, f):
        return self.components(f, self._terrain, self.tiles)

    def loaddata(self, data):
        random.setstate(data['random'])
        self._initgrid(data['gridsize'])
        self.spin, self.cells, self.tilt = [data[k] for k in ['spin', 'cells', 'tilt']]
        self.tiles = data['tiles']
        self._terrain = self.terrain(self.grid, self.tiles)
        self.shapes = data['shapes']
        self.populated = data['population']
        self.agricultural = data['agricultural']
        self._glaciationt = data['glaciationtime']
        self.initindexes()

    def load(self, filename):
        self.loaddata(Data.load(filename))

    def savedata(self):
        return Data.savedata(random.getstate(), self._grid.size, 0, self.spin, self.cells, self.tilt, None, None, None, self.tiles, self.shapes, self._glaciationt, self.populated, self.agricultural, True, True)

    def save(self, filename):
        Data.save(filename, self.savedata())
