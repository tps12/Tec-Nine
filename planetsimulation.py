from cProfile import Profile
from itertools import combinations
from math import asin, acos, atan2, pi, exp, sqrt, sin, cos
import random
from time import time

from numpy.linalg import norm

from grid import Grid
from hexadjacency import *
from climatemethod import climate
from erodemethod import erode
from movemethod import move
from planetdata import Data
from pointtree import PointTree
from rock import igneous, sedimentary, metamorphic
from shape import *
from splitmethod import split
from tile import *
from timing import Timing

class TileMovement(object):
    def __init__(self, sources, speed):
        self.sources = sources
        self.speed = speed

class NextTileValue(object):
    def __init__(self, movements):
        self._substances = [[s.substance for s in m.sources] for m in movements]
        self._build = 0

    def build(self, amount):
        self._build = amount

    def apply(self, tile):
        tile.mergesources(self._substances)
        tile.build(self._build, PlanetSimulation.seafloor())

class PlanetSimulation(object):
    temprange = (-25.0, 50.0)

    def __init__(self, r, gridsize, spin, cells, tilt, landr, dt):
        """Create a simulation for a planet with the given characteristics. """

        self._timing = Timing()

        initt = self._timing.routine('simulation setup')

        self.spin, self.cells, self.tilt = spin, cells, tilt

        # max speed is 100km per million years
        self._dp = 100.0/r * dt

        self._build = dt/5.0
        self._erode = dt

        tilearea = 4 * pi * r**2

        initt.start('building grid')

        self._initgrid(gridsize)

        self.tiles = {}
        for v in self._grid.faces:
            x, y, z = v
            lat = 180/pi * atan2(y, sqrt(x*x + z*z))
            lon = 180/pi * atan2(-x, z)
            self.tiles[v] = Tile(lat, lon)

        initt.start('building indexes')

        self.initindexes()

        initt.start('creating initial landmass')

        tilearea /= len(self._indexedtiles)

        # the numerator of the split probability, where
        # the number of tiles in the shape is the denomenator:
        # a 50M km^2 continent has a 50/50 chance of splitting in a given step
        self._splitnum = 25e6/tilearea

        # initial location
        p = [random.uniform(-1, 1) for i in range(3)]
        p /= norm(p)

        # 0 velocity vector
        v = (0, 0, 0)

        # orienting point
        o = [0, 0, 0]
        mini = min(range(len(p)), key=lambda i: abs(p[i]))
        o[mini] = 1 if p[mini] < 0 else -1

        shape = [(landr*random.uniform(0.9,1.1)*cos(th),
                  landr*random.uniform(0.9,1.1)*sin(th))
                 for th in [i*pi/8 for i in range(16)]]

        shape = Shape(shape, p, o, v).projection()

        self._shapes = [Group([t for t in self.tiles.itervalues() if shape.contains(t.vector)], v)]

        # initial landmass starts at elevation based on distance from center
        c = self._indexedtiles[self._index.nearest(p)[0]]
        r2 = landr*landr

        # on land, one random tile is the center of a felsic chunk
        f = random.choice(self._shapes[0].tiles)

        for t in self._indexedtiles:
            if t in self._shapes[0].tiles:
                dc = t.distance(c)
                df = t.distance(f)

                r = igneous.extrusive(max(0.5, 1 - df*df/r2))
                h = 1 - dc*dc/r2

                t.emptyland(r, h)
            else:
                t.emptyocean(self.seafloor())

        for t in self.tiles.itervalues():
            t.climate = None

        initt.done()

        self._atmosphere = self._life = False

        self._climatemappings = {}
        self._climateprof = None

        self.dirty = True

    def _initgrid(self, gridsize):
        grid = Grid()
        while grid.size < gridsize:
            grid = Grid(grid)
            grid.populate()
        self._grid = grid

    @property
    def grid(self):
        return self._grid

    @property
    def haslife(self):
        return self._life

    @staticmethod
    def seafloor():
        return igneous.extrusive(0.5)

    def initindexes(self):
        self._indexedtiles = []
        for t in self.tiles.itervalues():
            self._indexedtiles.append(t)

        self.adj = Adjacency(self._grid)
                
        self._tileadj = dict()
        for v in self._grid.faces:
            self._tileadj[self.tiles[v]] = set([self.tiles[nv] for nv in self.adj[v]])
       
        self._index = PointTree(dict([[self._indexedtiles[i].vector, i]
                                      for i in range(len(self._indexedtiles))]))

    def nearest(self, loc):
        return self._indexedtiles[self._index.nearest(loc)[0]]

    @property
    def continents(self):
        return len(self._shapes)

    @property
    def land(self):
        return int(100.0*sum([len(s.tiles) for s in self._shapes])/len(self._indexedtiles) + 0.5)

    def loaddata(self, data):
        random.setstate(data['random'])
        self._initgrid(data['gridsize'])
        self.spin, self.cells, self.tilt = [data[k] for k in ['spin', 'cells', 'tilt']]
        self._dp = data['dp']
        self._build = data['build']
        self._splitnum = data['splitnum']
        self.tiles = data['tiles']
        self._shapes = data['shapes']
        self._atmosphere = data['hasatm']
        self._life = data['haslife']

        self.initindexes()
        self.dirty = True

    def load(self, filename):
        self.loaddata(Data.load(filename))

    def savedata(self):
        return Data.savedata(random.getstate(), self._grid.size, 0, self.spin, self.cells, self.tilt, self._dp, self._build, self._splitnum, self.tiles, self._shapes, 0, {}, set(), self._atmosphere, self._life)

    def save(self, filename):
        Data.save(filename, self.savedata())

    def update(self):
        """Update the simulation by one timestep."""

        stept = self._timing.routine('simulation step')

        stept.start('determining tile movements')

        old = set([t for shape in self._shapes for t in shape.tiles])
        new = dict()

        overlapping = {}
        for t in self._indexedtiles:
            overlapping[t] = []

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
                    new[dest].append(TileMovement(sources, speed))
                else:
                    new[dest] = [TileMovement(sources, speed)]
                overlapping[dest].append(i)

        stept.start('applying tile movements')

        collisions = {}

        newe = {}

        seen = set()
        for dest, movements in new.items():
            # get all the source tiles contributing to this one
            newe[dest] = NextTileValue(movements)
            if not dest in seen:
                try:
                    old.remove(dest)
                except KeyError:
                    # calculate the amount to build up the leading edge
                    newe[dest].build(self._build * sum([m.speed for m in movements])/len(movements))
                seen.add(dest)

            for pair in combinations(overlapping[dest], 2):
                if pair in collisions:
                    collisions[pair] += 1
                else:
                    collisions[pair] = 1

        # apply the new values
        for t, e in newe.items():
            e.apply(t)

        # clear out abandoned tiles
        for t in old:
            t.emptyocean(self.seafloor())

        # record each continent's total pre-erosion above-sea size
        heights = [sum([t.elevation for t in s.tiles]) for s in self._shapes]

        if self._atmosphere:
            stept.start('"simulating" climate')

            seasons = [0.1*v for v in range(-10,10,5) + range(10,-10,-5)]
            c = climate(self.tiles, self.adj, seasons, self.cells, self.spin, self.tilt, self.temprange, 0.5, self._life, self._climatemappings, self._climateprof)

            if self._climateprof:
                self._climateprof.dump_stats('climate.profile')

            for v, tile in self.tiles.iteritems():
                tile.climate = c[v]['classification']

            stept.start('determining erosion')

            erosion = erode(self.tiles, self.adj)

            for t in self.tiles.itervalues():
                t.erode(erosion, self._erode)

            for t in self.tiles.itervalues():
                # if the tile is in at least one shape, apply the erosion materials
                if len(overlapping[t]) > 0:
                    if len(erosion[t].materials) > 0:
                        t.deposit(sedimentary.deposit(erosion[t].materials, self._life, False, t.climate))
                # otherwise, require a certain threshold
                elif sum([m.amount for m in erosion[t].materials]) > 1.5:
                    t.deposit(sedimentary.deposit(erosion[t].materials, self._life, True, t.climate))
                    sourceshapes = set()
                    for e in erosion[t].sources:
                        for shape in overlapping[e]:
                            sourceshapes.add(shape)
                    for s in sourceshapes:
                        if not t in self._shapes[s].tiles:
                            self._shapes[s].tiles.append(t)
                    overlapping[t] = list(sourceshapes)
            if not self._life:
                self._life = random.random() < 0.05
        elif random.random() < 0.05:
            self._atmosphere = True

        stept.start('applying isostatic effects')

        for s, h in zip(self._shapes, heights):
            dh = (h - sum([t.elevation for t in s.tiles]))/float(len(s.tiles))
            for t in s.tiles:
                t.isostasize(dh)

        stept.start('performing random intrusions')

        for t in self.tiles.itervalues():
            if t.subduction > 0:
                if random.random() < 0.1:
                    t.intrude(igneous.intrusive(max(0, min(1, random.gauss(0.85, 0.15)))))
                    t.transform(metamorphic.contact(t.substance[1], t.intrusion))

        stept.start('applying regional metamorphism')

        for t in self.tiles.itervalues():
            t.transform(metamorphic.regional(t.substance[1], t.subduction > 0))

        for t in self.tiles.itervalues():
            t.cleartemp()

        stept.start('merging overlapping shapes')

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

        stept.start('randomly splitting shapes')

        # occaisionally split big shapes
        for i in range(len(self._shapes)):
            if random.uniform(0,1) > self._splitnum / len(self._shapes[i].tiles):
                self._shapes[i:i+1] = [Group(ts, self._shapes[i].v + v * self._dp)
                                       for ts, v in split(self._shapes[i].tiles)]

        stept.done()

        self.dirty = True
