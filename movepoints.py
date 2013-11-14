from itertools import combinations
from math import asin, acos, atan2, pi, exp, sqrt, sin, cos
from multiprocessing import cpu_count, Pool
import random
from time import time

from numpy import cross
from numpy.linalg import norm

from latrange import *
from pointtree import PointTree
from sphericalpolygon import *

from grid import Grid
from hexadjacency import *
from shape import *
from movemethod import move, average, rotate
from tile import *

class MovePoints(object):
    def __init__(self, r):
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

        adj = Adjacency(self._grid)
        self._adj = dict()
        for v in self._grid.faces:
            self._adj[self.tiles[v]] = set([self.tiles[nv] for nv in adj[v]])

        self.reset(0, 1)

    @property
    def grid(self):
        return self._grid

    def reset(self, direction, speed):
        # initial location
        p = [random.uniform(-1, 1) for i in range(3)]
        p /= norm(p)

        # orienting point
        o = [0, 0, 0]
        mini = min(range(len(p)), key=lambda i: abs(p[i]))
        o[mini] = 1 if p[mini] < 0 else -1

        # velocity vector
        v = cross(p, o)
        v /= norm(v)
        v *= speed*pi/180

        r = 1.145
        shape = Shape([(r*random.uniform(0.9,1.1)*cos(th),
                       r*random.uniform(0.9,1.1)*sin(th))
                       for th in [i*pi/8 for i in range(16)]],
                       p, o, v).projection()

        for t in self.tiles.itervalues():
            t.bottom = 0
            t.layers = [Layer('T', 1)] if shape.contains(t.vector) else []
            t.limit()

        self._indexedtiles = []
        for t in self.tiles.itervalues():
            self._indexedtiles.append(t)

        self._index = PointTree(dict([[self._indexedtiles[i].vector, i]
                                      for i in range(len(self._indexedtiles))]))
    
        self._direction = direction
        self._velocity = v

    def step(self):
        start = time()

        group = [t for t in self.tiles.itervalues() if t.elevation == 1]
        for t in self._indexedtiles:
            t.layers = []
        for t in group:
            t.layers = [Layer('M', 2)]

        group, v = move(self._indexedtiles,
                        group,
                        self._velocity,
                        self._adj,
                        self._index)
        for t, ts in group.iteritems():
            t.layers = [Layer('T', 1)]

        self._velocity = v

        self.time = time() - start

    def direction(self, value):
        a = average([t.vector for t in self.tiles.itervalues() if t.elevation == 1])
        a /= norm(a)
        self._velocity = rotate(self._velocity, a, value - self._direction)
        self._direction = value

    def speed(self, value):
        self._velocity /= norm(self._velocity)
        self._velocity *= value*pi/180

    @property
    def count(self):
        return sum([t.elevation for t in self.tiles.itervalues()])
