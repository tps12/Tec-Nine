from cPickle import dump, load
from itertools import combinations
from math import asin, acos, atan2, pi, exp, sqrt, sin, cos
import random
from time import time

from numpy import *
from numpy.linalg import *

from adjacency import *
from movemethod import move
from pointtree import PointTree
from shape import *
from splitmethod import split
from tile import *

class ErodedMaterial(object):
    def __init__(self, amount, sources=None):
        self.amount = amount
        self.sources = sources

class Group(object):
    def __init__(self, tiles, v):
        self.tiles = tiles
        self.v = v

class PlanetSimulation(object):
    def __init__(self, r, dt):
        """Create a simulation for a planet of radius r km and timesteps of dt
        million years.
        """
        # max speed is 100km per million years
        self._dp = 100.0/r * dt

        self._erode = dt

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

        self.adj = Adjacency(self.tiles)
                
        xmax = max([len(self.tiles[i]) for i in range(len(self.tiles))])

        dimensions = xmax, len(self.tiles)
   
        # initial location
        p = (0, 1, 0)

        # 0 velocity vector
        v = (0, 0, 0)

        # orienting point
        o = (1, 0, 0)

        r = 1.145
        shape = [(r*random.uniform(0.9,1.1)*cos(th),
                  r*random.uniform(0.9,1.1)*sin(th))
                 for th in [i*pi/8 for i in range(16)]]

        shape = Shape(shape, p, o, v).projection()

        self._shapes = [Group([t for lat in self.tiles for t in lat if shape.contains(t.vector)], v)]

        self._indexedtiles = []
        for lat in self.tiles:
            for t in lat:
                i = len(self._indexedtiles)
                self._indexedtiles.append(t)

        self._index = PointTree(dict([[self._indexedtiles[i].vector, i]
                                      for i in range(len(self._indexedtiles))]))

        self.dirty = True

    def update(self):
        """Update the simulation by one timestep."""
        for t in self._indexedtiles:
            t.value = 0

        for i in range(len(self._shapes)):
            group, v = move(self._indexedtiles,
                            self._shapes[i].tiles,
                            self._shapes[i].v,
                            self._index)
            self._shapes[i] = Group(group.keys(), v)
            for t in self._shapes[i].tiles:
                t.value = min(t.value + 1, 10)

        # occaisionally split big shapes
        for i in range(len(self._shapes)):
            if random.uniform(0,1) > 500/float(len(self._shapes[i].tiles)):
                self._shapes[i:i+1] = [Group(ts, self._shapes[i].v + v/20) for ts, v in split(self._shapes[i].tiles)]

        self.dirty = True
