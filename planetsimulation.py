from cPickle import dump, load
from itertools import combinations
from math import asin, acos, atan2, pi, exp, sqrt, sin, cos
import random
from time import time

from adjacency import *
from climatemethod import climate
from erodemethod import erode
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
    EXTENSION = '.tec9'

    cells = 3
    spin = 1.0
    tilt = 23

    temprange = (-25.0, 50.0)

    def __init__(self, r, dt):
        """Create a simulation for a planet of radius r km and timesteps of dt
        million years.
        """
        # max speed is 100km per million years
        self._dp = 100.0/r * dt

        self._build = 1.25 * dt

        tilearea = 4 * pi * r**2

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

        tilearea /= len(self._indexedtiles)

        # the numerator of the split probability, where
        # the number of tiles in the shape is the denomenator:
        # a 50M km^2 continent has a 50/50 chance of splitting in a given step
        self._splitnum = 25e6/tilearea

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
        for t in self._shapes[0].tiles:
            t.value = 1

        self.dirty = True

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

    @property
    def continents(self):
        return len(self._shapes)

    @property
    def land(self):
        return int(100.0*sum([len(s.tiles) for s in self._shapes])/len(self._indexedtiles) + 0.5)

    def data(self):
        data = dict()
        data['random'] = random.getstate()
        data['dp'] = self._dp
        data['build'] = self._build
        data['splitnum'] = self._splitnum
        data['tiles'] = self.tiles
        data['shapes'] = [([self._indexedtiles.index(t) for t in s.tiles], s.v) for s in self._shapes]
        return data

    def setdata(self, data):
        random.setstate(data['random'])
        self._dp = data['dp']
        self._build = data['build']
        self._splitnum = data['splitnum']
        self.tiles = data['tiles']
        self.initindexes()
        self._shapes = [Group([self._indexedtiles[i] for i in tis], v) for (tis, v) in data['shapes']]
        self.dirty = True

    def load(self, filename):
        with open(filename, 'r') as f:
            self.setdata(load(f))

    def save(self, filename):
        if filename[-len(self.EXTENSION):] != self.EXTENSION:
            filename += self.EXTENSION
        with open(filename, 'w') as f:
            dump(self.data(), f, 0)

    def update(self):
        """Update the simulation by one timestep."""

        old = set([t for shape in self._shapes for t in shape.tiles])
        new = dict()

        overlapping = {}
        for t in self._indexedtiles:
            overlapping[t] = []
            t.dv = []

        for i in range(len(self._shapes)):
            speed = norm(self._shapes[i].v)
            group, v = move(self._indexedtiles,
                            self._shapes[i].tiles,
                            self._shapes[i].v,
                            self._tileadj,
                            self._index)
            self._shapes[i] = Group(group.keys(), v)
            for dest, sources in group.items():
                if dest in new:
                    new[dest].append((sources,speed))
                else:
                    new[dest] = [(sources,speed)]
                overlapping[dest].append(i)

        collisions = {}

        seen = set()
        for dest, sourcelists in new.items():
            dest.value = sum([sum([t.value for t in sources])/len(sources) for sources, speed in sourcelists])
            if not dest in seen:
                try:
                    old.remove(dest)
                except KeyError:
                    dest.value += self._build * sum([speed for sources, speed in sourcelists])/len(sourcelists)
                seen.add(dest)
            dest.value = min(10, dest.value)

            for pair in combinations(overlapping[dest], 2):
                if pair in collisions:
                    collisions[pair] += 1
                else:
                    collisions[pair] = 1

        for t in old:
            t.value = 0

        seasons = [0.1*v for v in range(-10,10,5) + range(10,-10,-5)]
        c = climate(self.tiles, self.adj, seasons, self.cells, self.spin, self.tilt, self.temprange) 

        erosion = erode(self.tiles, self.adj, overlapping, c)

        for t in [t for lat in self.tiles for t in lat]:
            t.dv = erosion[t]

        for i in range(len(self.tiles)):
            for j in range(len(self.tiles[i])):
                tile = self.tiles[i][j]
                if len(overlapping[tile]) > 0:
                    tile.value += sum([e.amount for e in tile.dv])
                elif sum([e.amount for e in tile.dv]) > 1.5:
                    tile.value = sum([e.amount for e in tile.dv])
                    sources = set()
                    for e in tile.dv:
                        for s in e.sources:
                            sources.add(s)
                    for s in sources:
                        if not tile in self._shapes[s].tiles:
                            self._shapes[s].tiles.append(tile)
                    overlapping[tile] = list(sources)

        # merge shapes that overlap a lot
        groups = []
        for pair, count in collisions.items():
            if count > min([len(self._shapes[i].tiles) for i in pair])/10:
                for group in groups:
                    if pair[0] in group:
                        group.add(pair[1])
                        break
                    elif pair[1] in group:
                        group.add(pair[0])
                        break
                else:
                    groups.append(set(pair))

        gone = []
        for group in groups:
            largest = max(group, key=lambda i: len(self._shapes[i].tiles))
            tiles = list(self._shapes[largest].tiles)
            v = array(self._shapes[largest].v) * len(tiles)
            for other in group:
                if other != largest:
                    v += array(self._shapes[other].v) * len(self._shapes[other].tiles)
                    tiles += self._shapes[other].tiles
                    gone.append(self._shapes[other])
            self._shapes[largest].tiles = list(set(tiles))
            v /= len(tiles)
            self._shapes[largest].v = v
        for s in gone:
            self._shapes.remove(s)

        # occaisionally split big shapes
        for i in range(len(self._shapes)):
            if random.uniform(0,1) > self._splitnum / len(self._shapes[i].tiles):
                self._shapes[i:i+1] = [Group(ts, self._shapes[i].v + v * self._dp)
                                       for ts, v in split(self._shapes[i].tiles)]

        self.dirty = True
