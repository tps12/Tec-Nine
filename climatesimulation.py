from cPickle import load
from math import pi, cos, isinf
from random import choice

from adjacency import *
from earth import Earth
from extrema import findextrema
from pointtree import PointTree
from tile import *

class ClimateSimulation(object):
    EXTENSION = '.tec9'

    def __init__(self, r):
        """Create a simulation for a planet of radius r km."""
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
        self.cells = 3

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

    def zonalpressure(self, lat):
        # low at 0 lat, high at +/- 90
        # other extrema in between if there are > 1 cells
        return -cos(2 * self._cells * lat * pi/180)

    def peaklatindices(self):
        # indices into self.tiles where the zonal pressure is maximized
        dlat = 90.0/self._cells
        indices = [min(range(len(self.tiles)/2), key=lambda y: abs(-self.tiles[y][0].lat - dlat * (2*i + 1)))
                    for i in range(self._cells/2 + 1)]

        indices += [[j for j in range(len(self.tiles)/2, len(self.tiles)) if self.tiles[j][0].lat == -self.tiles[i][0].lat][0]
                    for i in indices]
        return sorted(indices)

    def landseadistances(self):
        frontier = set()
        for t in self._indexedtiles:
            if t.value > 0:
                if any([n.value <= 0 for n in self._tileadj[t]]):
                    t.seadistance = 1
                    frontier.add(t)
                else:
                    t.seadistance = float('inf')
                t.landdistance = 0
            else:
                if any([n.value > 0 for n in self._tileadj[t]]):
                    t.landdistance = 1
                    frontier.add(t)
                else:
                    t.landdistance = float('inf')
                t.seadistance = 0

        while len(frontier) > 0:
            nextfrontier = set()
            while len(frontier) > 0:
                t = frontier.pop()
                for n in self._tileadj[t]:
                    if not isinf(t.seadistance):
                        n.seadistance = min([n.seadistance] +
                                            [nn.seadistance + 1 for nn in self._tileadj[n]])
                        if any([nn.seadistance == float('inf') for nn in self._tileadj[n]]):
                            nextfrontier.add(n)
                    if not isinf(t.landdistance):
                        n.landdistance = min([n.landdistance] +
                                            [nn.landdistance + 1 for nn in self._tileadj[n]])
                        if any([nn.landdistance == float('inf') for nn in self._tileadj[n]]):
                            nextfrontier.add(n)
            frontier = nextfrontier

    def extrema(self, peaklatindices):
        # in a "high" zone, maxima over oceans, minima over landmasses
        self.landseadistances()
        extrema = []

        for y in sorted(peaklatindices):
            bucket = dict()
            for x in findextrema(self.tiles[y], lambda a, b: a.seadistance > b.seadistance):
                bucket[self.tiles[y][x].vector] = self.tiles[y][x]
                self.tiles[y][x].pressure = 1
                found = x
            for x in findextrema(self.tiles[y], lambda a, b: a.landdistance > b.landdistance):
                bucket[self.tiles[y][x].vector] = self.tiles[y][x]
                self.tiles[y][x].pressure = -1
                found = x
            if len(bucket) == 1:
                # latitude is all-land or all-sea with only a single peak;
                # add in a fake one at the opposite longitude so the PointTree will work
                x = found - len(self.tiles[y])/2 # okay if it wraps around
                bucket[self.tiles[y][x].vector] = self.tiles[y][x]
                self.tiles[y][x].pressure = 0
            extrema.append(PointTree(bucket) if len(bucket) > 0 else None)

        return extrema

    def pressure(self):
        peaklatindices = self.peaklatindices()
        extrema = self.extrema(peaklatindices)
        
        for y in range(len(self.tiles)):
            b = min(range(len(peaklatindices)), key=lambda i: abs(peaklatindices[i] - y))
            for t in self.tiles[y]:
                z = self.zonalpressure(t.lat)

                if extrema[b] is None:
                    t.pressure = 0#z ** 3
                else:
                    s, pt = extrema[b].nearest(t.vector, score=True)[0]

                    d = t.distance(pt)
                    #p = z ** 2
                    p = pt.pressure * (cos(min(8*d, pi)) + 1)/2
                    
                    t.pressure = p

    @property
    def cells(self):
        return self._cells

    @cells.setter
    def cells(self, value):
        self._cells = value
        self.pressure()

    @property
    def earthavailable(self):
        return Earth.available()

    def earth(self):
        earth = Earth()
        for t in self._indexedtiles:
            t.value = earth.sample(t.lat, t.lon) / 900.0
            if t.value < 0:
                t.value = 0
        self.pressure()

    def setdata(self, data):
        self.tiles = data['tiles']
        self.initindexes()

    def load(self, filename):
        with open(filename, 'r') as f:
            self.setdata(load(f))
        self.pressure()
