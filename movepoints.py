from cPickle import dump, load
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

from adjacency import *
from shape import *
from movemethod import move, average, rotate
from tile import *

def _setlat(lat, shape):
    """Set tile values for the given latitude array."""
    for x in range(len(lat)):
        lat[x].bottom = 0
        lat[x].layers = [Layer('T', 1)] if shape.contains(lat[x].vector) else []
    return lat

class MovePoints(object):
    def __init__(self, r):

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

        adj = Adjacency(self.tiles)
        self._adj = dict()
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                self._adj[self.tiles[y][x]] = [self.tiles[j][i] for i, j in adj[(x,y)]]

        self.reset(0, 1)

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

        self.tiles = [_setlat(lat, shape) for lat in self.tiles]

        self._indexedtiles = []
        for lat in self.tiles:
            for t in lat:
                i = len(self._indexedtiles)
                self._indexedtiles.append(t)

        self._index = PointTree(dict([[self._indexedtiles[i].vector, i]
                                      for i in range(len(self._indexedtiles))]))
    
        self._direction = direction
        self._velocity = v

    def step(self):
        start = time()

        group = [t for lat in self.tiles for t in lat if t.elevation == 1]
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
        a = average([t.vector for lat in self.tiles for t in lat if t.elevation == 1])
        a /= norm(a)
        self._velocity = rotate(self._velocity, a, value - self._direction)
        self._direction = value

    def speed(self, value):
        self._velocity /= norm(self._velocity)
        self._velocity *= value*pi/180

    @property
    def count(self):
        return sum([1 for lat in self.tiles for t in lat if t.elevation == 1])
