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
from movemethod import move
from holemethod import findholes
from tile import *

def _setlat(lat, shape):
    """Set tile values for the given latitude array."""
    for x in range(len(lat)):
        lat[x].value = 1 if shape.contains(lat[x].vector) else 0
    return lat

class FillHoles(object):
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

        self.reset(False, True, True)

    def reset(self, move, small, large):
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
    
        if move:
            self.move(v)

        if small:
            for t in [t for lat in self.tiles for t in lat if t.value == 1]:
                if random.random() < 0.1:
                    t.value = 0

        self.findholes()

    def findholes(self):
        start = time()

        group = [t for lat in self.tiles for t in lat if t.value == 1]

        holes, boundary = findholes(self._indexedtiles,
                                    group,
                                    self._adj,
                                    self._index)

        for t in holes:
            t.value = 2
        for t in boundary:
            t.value = 3

        self.time = time() - start

    def move(self, velocity):
        group = [t for lat in self.tiles for t in lat if t.value == 1]
        for t in self._indexedtiles:
            t.value = 0

        group, v = move(self._indexedtiles,
                        group,
                        velocity,
                        self._adj,
                        self._index)
        for t, ts in group.iteritems():
            t.value = 1

    @property
    def count(self):
        return sum([1 for lat in self.tiles for t in lat if t.value == 1])
