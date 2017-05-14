import random
import time

from numpy import cross
from numpy.linalg import norm

from climatemethod import ClimateInfo
from grid import Grid
from hexadjacency import Adjacency
from racinatemethod import racinate
from rock import igneous
from shape import Shape
from tile import *

class Continent(object):
    def __init__(self, center, avgradius):
        self.center = center
        self.avgradius = avgradius
        self.orientingpt = [0, 0, 0]
        mini = min(range(3), key=lambda i: abs(self.center[i]))
        self.orientingpt[mini] = 1 if self.center[mini] < 0 else -1
        self.outer = Shape([(self.avgradius*random.uniform(0.9,1.1)*cos(th),
                             self.avgradius*random.uniform(0.9,1.1)*sin(th))
                            for th in [i*pi/8 for i in range(16)]],
                           self.center, self.orientingpt, (0,0,0)).projection()
        self.inner = Shape([(0.65*self.avgradius*random.uniform(0.9,1.1)*cos(th),
                             0.65*self.avgradius*random.uniform(0.9,1.1)*sin(th))
                            for th in [i*pi/8 for i in range(16)]],
                           self.center, self.orientingpt, (0,0,0)).projection()

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
            lat = 180/pi * atan2(y, sqrt(x*x + z*z))
            lon = 180/pi * atan2(-x, z)
            self.tiles[v] = Tile(lat, lon)

        for t in self.tiles.itervalues():
            t.emptyocean(self.seafloor())
        self.populated = set()
        self.races = [self.populated]
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
        p2 = [-p1i for p1i in p1]

        self.continents = [Continent(p, r) for p, r in [(p1, 0.75), (p2, 0.5)]]

        for t in self.tiles.itervalues():
            if any([c.outer.contains(t.vector) for c in self.continents]):
                t.bottom = 0
                t.layers = [Layer('T', 1)]
                t.limit()
                t.climate = ClimateInfo(None, None, u'Cw', None)
                if not any([c.inner.contains(t.vector) for c in self.continents]):
                    self.populated.add(t)
            else:
                t.emptyocean()
                t.climate = None

    def isolate(self):
        for c in self.continents:
            th0 = random.uniform(0, pi)
            swath = Shape([(1.2*c.avgradius*cos(th), 1.2*c.avgradius*sin(th))
                           for th in [th0, th0 + pi/12, th0 + pi, th0 + pi + pi/12]],
                          c.center, c.orientingpt, (0,0,0)).projection()
            k = random.choice([u'BW', u'ET'])
            for t in self.tiles.itervalues():
                if swath.contains(t.vector) and c.outer.contains(t.vector):
                    t.climate = ClimateInfo(None, None, k, None)
                    if t in self.populated:
                        self.populated.remove(t)
        self.races = racinate(self.tiles.values(), self._tileadj, self.populated, self.range)

    @property
    def grid(self):
        return self._grid

    @property
    def peoples(self):
        return len(self.races)

    @staticmethod
    def seafloor():
        return igneous.extrusive(0.5)
