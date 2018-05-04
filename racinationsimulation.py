import random
import time

from numpy import array, cross
from numpy.linalg import norm

from climatemethod import ClimateInfo
from grid import Grid
from hexadjacency import Adjacency
from movemethod import rotate
import race
from racinatemethod import racinate
from rock import igneous
from sphericalpolygon import SphericalPolygon
from tile import *

class Continent(object):
    def __init__(self, center, avgradius):
        self.center = center
        self.avgradius = avgradius
        self.orientingpt = [0, 0, 0]
        mini = min(range(3), key=lambda i: abs(self.center[i]))
        self.orientingpt[mini] = 1 if self.center[mini] < 0 else -1
        self.outer = SphericalPolygon([rotate(rotate(self.center, self.orientingpt, self.avgradius*random.uniform(0.9,1.1)), self.center, th)
                                       for th in [i*pi/8 for i in range(16)]])
        self.inner = SphericalPolygon([rotate(rotate(self.center, self.orientingpt, 0.65*self.avgradius*random.uniform(0.9,1.1)), self.center, th)
                                       for th in [i*pi/8 for i in range(16)]])

class RacinationSimulation(object):
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

        for t in self.tiles.values():
            t.emptyocean(self.seafloor())
        self.populated = {}
        self.range = 6

        self.adj = Adjacency(self._grid)
        self.initindexes()

        self.reset()

    def initindexes(self):
        self._tileadj = dict()
        for v in self._grid.faces:
            self._tileadj[self.tiles[v]] = set([self.tiles[nv] for nv in self.adj[v]])

    def reset(self):
        # initial location
        p1 = [random.uniform(-1, 1) for i in range(3)]
        p1 /= norm(p1)
        p2 = array([-p1i for p1i in p1])

        self.continents = [Continent(p, r) for p, r in [(p1, 0.75), (p2, 0.5)]]

        h = race.Heritage('people')
        for t in self.tiles.values():
            if any([c.outer.contains(t.vector) for c in self.continents]):
                t.bottom = 0
                t.layers = [Layer('T', 1)]
                t.limit()
                t.climate = ClimateInfo(None, None, u'Cw', None)
                if not any([c.inner.contains(t.vector) for c in self.continents]):
                    self.populated[t] = h
            else:
                t.emptyocean()
                t.climate = None
            t.seasons = None

    def isolate(self):
        for c in self.continents:
            th0 = random.uniform(0, pi)
            swath = SphericalPolygon([rotate(rotate(c.center, c.orientingpt, 1.2*c.avgradius), c.center, th)
                                      for th in [th0, th0 + pi/12, th0 + pi, th0 + pi + pi/12]], c.center)
            k = random.choice([u'BW', u'ET'])
            for t in self.tiles.values():
                if swath.contains(t.vector) and c.outer.contains(t.vector):
                    t.climate = ClimateInfo(None, None, k, None)
                    if t in self.populated:
                        del self.populated[t]
        racinate(self.tiles.values(), self._tileadj, self.populated, lambda: 'people', set(), self.range)

    @property
    def grid(self):
        return self._grid

    @property
    def peoples(self):
        return len({p for p in self.populated.values()})

    @staticmethod
    def seafloor():
        return igneous.extrusive(0.5)
