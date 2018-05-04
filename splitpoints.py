from itertools import combinations
from math import asin, acos, atan2, pi, exp, sqrt, sin, cos
from multiprocessing import cpu_count, Pool
import random

from numpy.linalg import norm

from grid import Grid
from movemethod import rotate
from sphericalpolygon import SphericalPolygon
from splitmethod import split
from tile import *

class SplitPoints(object):
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

        self.reset()

    @property
    def grid(self):
        return self._grid

    def reset(self):
        # initial location
        p = [random.uniform(-1, 1) for i in range(3)]
        p /= norm(p)

        # 0 velocity vector
        v = (0, 0, 0)

        # orienting point
        o = [0, 0, 0]
        mini = min(range(len(p)), key=lambda i: abs(p[i]))
        o[mini] = 1 if p[mini] < 0 else -1

        r = 1.145
        shape = SphericalPolygon([rotate(rotate(p, o, r*random.uniform(0.9,1.1)), p, th)
                                  for th in [i*pi/8 for i in range(16)]])

        for t in self.tiles.values():
            t.bottom = 0
            t.layers = [Layer('T', 1)] if shape.contains(t.vector) else []
            t.limit()

        self.split()

    def split(self):
        a, b = [tiles for (tiles, v) in split([t for t in self.tiles.values() if t.elevation == 1])]
        for t in a:
            t.layers = [Layer('R', 1)]
        for t in b:
            t.layers = [Layer('B', 1)]

    def iterate(self, red):
        match = 'R' if red else 'B'
        for t in self.tiles.values():
            t.layers = [Layer('T', 1)] if len(t.layers) > 0 and t.layers[0].rock == match else []
            t.limit()
        self.split()
