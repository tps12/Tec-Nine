from cPickle import load
from math import pi, cos

from adjacency import *
from earth import Earth
from pointtree import PointTree
from tile import *

class ClimateSimulation(object):
    EXTENSION = '.tec9'

    def __init__(self, r):
        """Create a simulation for a planet of radius r km."""
        degrees = 2

        self.tiles = []
        for lat in range(-89, 91, degrees):
            r = cos(lat * pi/180)
            row = []
            d = 2 / r
            lon = d/2
            while lon <= 180:
                flat = float(lat)
                row = ([Tile(flat, -lon)] +
                       row +
                       [Tile(flat, lon)])
                lon += d
            self.tiles.append(row)

        self.initindexes()
        self.cells = 3

    def initindexes(self):
        self._indexedtiles = []
        for lat in self.tiles:
            for t in lat:
                self._indexedtiles.append(t)

        self.adj = Adjacency(self.tiles)
                
        self._tileadj = dict()
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                self._tileadj[self.tiles[y][x]] = [self.tiles[j][i] for i, j in self.adj[(x,y)]]
       
        self._index = PointTree(dict([[self._indexedtiles[i].vector, i]
                                      for i in range(len(self._indexedtiles))]))

    def pressure(self):
        # low at 0 lat, high at +/- 90
        # other extrema in between if there are > 1 cells
        p = lambda lat: -cos(2 * self._cells * lat * pi/180)
        for t in self._indexedtiles:
            t.pressure = p(t.lat)

    @property
    def cells(self):
        return self._cells

    @cells.setter
    def cells(self, value):
        self._cells = value
        self.pressure()

    @property
    def earthavailable(self):
        return Earth.available()

    def earth(self):
        earth = Earth()
        for t in self._indexedtiles:
            t.value = earth.sample(t.lat, t.lon) / 900.0
            if t.value < 0:
                t.value = 0

    def setdata(self, data):
        self.tiles = data['tiles']
        self.initindexes()

    def load(self, filename):
        with open(filename, 'r') as f:
            self.setdata(load(f))
        self.pressure()
