from itertools import combinations
from math import asin, acos, atan2, pi, exp, sqrt, sin, cos
from multiprocessing import cpu_count, Pool
import random

from numpy.linalg import norm

from latrange import *
from sphericalpolygon import *

from adjacency import *
from shape import *
from splitmethod import split
from tile import *

def _setlat(lat, shape):
    """Set tile values for the given latitude array."""
    for x in range(len(lat)):
        lat[x].bottom = 0
        lat[x].layers = [Layer('T', 1)] if shape.contains(lat[x].vector) else []
        lat[x].limit()
    return lat

class SplitPoints(object):
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

        self.reset()

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
        shape = Shape([(r*random.uniform(0.9,1.1)*cos(th),
                       r*random.uniform(0.9,1.1)*sin(th))
                       for th in [i*pi/8 for i in range(16)]],
                       p, o, v).projection()

        self.tiles = [_setlat(lat, shape) for lat in self.tiles]
        self.split()

    def split(self):
        a, b = [tiles for (tiles, v) in split([t for lat in self.tiles for t in lat if t.elevation == 1])]
        for t in a:
            t.layers = [Layer('R', 1)]
        for t in b:
            t.layers = [Layer('B', 1)]

    def iterate(self, red):
        match = 'R' if red else 'B'
        for lat in self.tiles:
            for t in lat:
                t.layers = [Layer('T', 1)] if len(t.layers) > 0 and t.layers[0].rock == match else []
                t.limit()
        self.split()
