from cPickle import load
from math import pi, cos, isinf, exp
from random import choice

from adjacency import *
from climateclassification import ClimateClassification
from earth import Earth
from extrema import findextrema
from pointtree import PointTree
from tile import *

def distance(c1, c2):
    lat1, lon1 = [c * pi/180 for c in c1]
    lat2, lon2 = [c * pi/180 for c in c2]

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * atan2(sqrt(a), sqrt(1-a))

def bearing(c1, c2):
    lat1, lon1 = [c * pi/180 for c in c1]
    lat2, lon2 = [c * pi/180 for c in c2]

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    theta = atan2(sin(dlon) * cos(lat2),
                  cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon))
    return (theta * 180/pi) % 360

class ClimateDict(object):
    def __init__(self, dimensions):
        self._xmax, self._ymax = dimensions
        self._list = [None for i in range(self._xmax * self._ymax)]
        self.clear()

    def _index(self, p):
        return p[0] + p[1] * self._xmax

    def __getitem__(self, p):
        isset, value = self._list[self._index(p)]
        if not isset:
            raise KeyError
        return value

    def __setitem__(self, p, value):
        self._list[self._index(p)] = True, value

    def __delitem__(self, p):
        self._list[self._index(p)] = None, None

    def clear(self):
        for i in range(len(self._list)):
            self._list[i] = None, None

    def iteritems(self):
        for y in range(self._ymax):
            for x in range(self._xmax):
                isset, value = self._list[self._index((x,y))]
                if isset:
                    yield (x,y), value

    def __len__(self):
        return len(list(self.iteritems()))

class ClimateSimulation(object):
    EXTENSION = '.tec9'

    spin = 1.0
    tilt = 23

    temprange = (-25.0, 50.0)
    breezedistance = 10
    
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

        self.initdicts()
        self._season = None
        self.cells = 3

    def initdicts(self):
        self.adj = Adjacency(self.tiles)
        
        xmax = max([len(self.tiles[i]) for i in range(len(self.tiles))])

        dimensions = xmax, len(self.tiles)
        (self.direction,
         self.precipitation,
         self.convective,
         self.seabased,
         self.temperature,
         self.pressure) = [ClimateDict(dimensions) for i in range(6)]

    @property
    def season(self):
        return self._season

    @season.setter
    def season(self, value):
        if self._season != value:
            self._season = value
            self.temperature.clear()
            self.convective.clear()
            self.seabased.clear()
            self.pressure.clear()

    def insolation(self, y):
        theta = 2 * pi * (y - len(self.tiles)/2)/len(self.tiles)/2
        theta += (self.tilt * pi/180) * self.season
        ins = max(0, cos(theta))
        return 0.5 + (ins - 0.5) * cos(self.tilt * pi/180)

    def resetclimate(self, direction, temperature, convective, seabased, pressure):
        res = max([len(r) for r in self.tiles]), len(self.tiles)
        
        c = self.cells

        e2 = 2 * exp(1)
        for y in range(res[1]):
            if direction:
                n = abs(y + 0.5 - res[1]/2)/(float(res[1]/2)/c)
                n = int(n) & 1
                n = n if y >= res[1]/2 else not n
                d = 180 - 180 * n

                s = self.spin
                ce = 2 * s * sin(2 * pi * (y - res[1]/2)/res[1]/2)
                d += atan2(ce, 1) * 180/pi
                d %= 360

            if temperature:
                ins = self.insolation(y)
            
            for x in range(len(self.tiles[y])):
                if direction:
                    self.direction[(x,y)] = d

                if temperature:                    
                    h = self.tiles[y][x].value
                    t = (ins * (1 - h/10.0) if h > 0 else ins)
                    self.temperature[(x,y)] = t

                if convective:
                    p = (cos((self.tiles[y][x].lat*2*c + self.tilt*self.season)*pi/180) + 1)/2
                    self.convective[(x,y)] = p

                if pressure:
                    h = self.tiles[y][x].value
                    if h > 0:
                        p = 0.5
                    else:
                        p = 1-(cos((self.tiles[y][x].lat*2*c + self.tilt*self.season)*pi/180) + 1)/2
                    self.pressure[(x,y)] = p
                    
                if direction or seabased:
                    self.seabased[(x,y)] = None

        if direction:
            self.sadj = {}
            for (x,y), ns in self.adj._adj.iteritems():
                c = self.tiles[y][x].lat, self.tiles[y][x].lon
                d = self.direction[(x,y)]
                self.sadj[(x,y)] = sorted(self.adj[(x,y)],
                                          key=lambda a: cos(
                                              (bearing(c,
                                                       (self.tiles[a[1]][a[0]].lat,
                                                        self.tiles[a[1]][a[0]].lon))
                                               - d) * pi / 180))
            self._definemapping()

        if direction or seabased:
            self._seabreeze()

        if direction or convective:
            self._totalprecipitation()

        self.dirty = True

    def _seabreeze(self):
        frontier = []
        d = 0
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                if self.tiles[y][x].value <= 0:
                    self.seabased[(x,y)] = d
                    frontier.append((x,y))
                    
        while d < self.breezedistance and frontier:
            d += 1
            frontier = self._propagate(frontier, d)

        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                seabased = self.seabased[(x,y)]
                if seabased is None:
                    h = 0
                else:
                    h = ((d - seabased)/float(d))**2
                p = min(1.0, h + self.convective[(x,y)])
                self.seabased[(x,y)] = h

    def _totalprecipitation(self):
        d = self.breezedistance
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                p = min(1.0, self.seabased[(x,y)] + self.convective[(x,y)])
                self.precipitation[(x,y)] = p
                
    def _propagate(self, sources, d):
        frontier = []
        for s in sources:
            for a in [p for (p,w) in self._destmap[s]]:
                if self.seabased[a] is None:
                    self.seabased[a] = d
                    frontier.append(a)
        return frontier

    def _definemapping(self):
        mapping = {}
        dests = {}

        def addmap(s, d, w):
            if d in mapping:
                l = mapping[d]
            else:
                l = []
                mapping[d] = l
            l.append((s,w))

            if s in dests:
                l = dests[s]
            else:
                l = []
                dests[s] = l
            l.append((d,w))

        seen = set()

        # map destinations for every tile
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                nws = [(a, cos((bearing(
                    (self.tiles[y][x].lat, self.tiles[y][x].lon),
                    (self.tiles[a[1]][a[0]].lat, self.tiles[a[1]][a[0]].lon))
                        - self.direction[(x,y)])*pi/180))
                       for a in self.sadj[(x,y)]]
                nws = [nw for nw in nws if nw[1] > 0]

                for n, w in nws:
                    addmap((x,y), n, w)
                    seen.add(n)

        # map from sources for any tile that hasn't been targeted
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                if (x,y) not in seen:
                    nws = [(a, -cos((bearing(
                        (self.tiles[y][x].lat, self.tiles[y][x].lon),
                        (self.tiles[a[1]][a[0]].lat, self.tiles[y][x].lon))
                            - self.direction[a])*pi/180))
                           for a in self.sadj[(x,y)]]
                    nws = [nw for nw in nws if nw[1] > 0]
                    
                    for n, w in nws:
                        addmap(n, (x,y), w)

        # normalize weights
        self._mapping = {}
        for (d, sws) in mapping.iteritems():
            t = sum([w for (s, w) in sws])
            self._mapping[d] = [(s, w/t) for (s,w) in sws]

        self._destmap = {}
        for (s, dws) in dests.iteritems():
            t = sum([w for (d, w) in dws])
            self._destmap[s] = [(d, w/t) for (d,w) in dws]

    def sources(self, p):
        return self._mapping[p]

    def average(self):
        self.update()
        return self._getaverage()

    def _getaverage(self):
        c = [[(0,0) for x in range(len(self.tiles[y]))]
             for y in range(len(self.tiles))]
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                c[y][x] = (self.tiles[y][x].value,
                           self.temperature[(x,y)],
                           self.precipitation[(x,y)])

        return c

    def classify(self, seasons = None):
        seasons = [-1, -0.5, 0, 0.5, 1, 0.5, 0, -0.5] if seasons is None else seasons
        ss = []
        for s in seasons:
            self.season = s
            ss.append(self.average())
            
        seasons = []
        for y in range(len(ss[0])):
            row = []
            for x in range(len(ss[0][y])):
                row.append((ss[0][y][x][0],
                            [ss[i][y][x][1:] for i in range(len(ss))]))
            seasons.append(row)

        c = ClimateClassification(seasons, self.temprange)
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                self.tiles[y][x].climate = c.climate[y][x][-1]
    
    def update(self):
        d, t, c, s, p = [not dic for dic in
                      self.direction, self.temperature, self.convective, self.seabased, self.pressure]
        if d or t or c or s or p:
            self.resetclimate(d, t, c, s, p)

    @property
    def cells(self):
        return self._cells

    @cells.setter
    def cells(self, value):
        self._cells = value
        self.classify()

    @property
    def earthavailable(self):
        return Earth.available()

    def earth(self):
        earth = Earth()
        for t in [t for lat in self.tiles for t in lat]:
            t.value = earth.sample(t.lat, t.lon) / 900.0
            if t.value < 0:
                t.value = 0
        self.initdicts()
        self.classify()

    def setdata(self, data):
        self.tiles = data['tiles']
        self.initdicts()

    def load(self, filename):
        with open(filename, 'r') as f:
            self.setdata(load(f))
        self.classify()
