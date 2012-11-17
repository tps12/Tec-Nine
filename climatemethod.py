from climateclassification import ClimateClassification
from math import exp, sin, cos, pi, atan2

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

class ClimateInfo(object):
    def __init__(self, temperature, precipitation, koeppen):
        self.temperature = temperature
        self.precipitation = precipitation
        self.koeppen = koeppen

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
        wasset = self._list[self._index(p)][0]
        self._list[self._index(p)] = True, value
        if not wasset:
            self._len += 1

    def __delitem__(self, p):
        self._list[self._index(p)] = None, None
        self._len -= 1

    def clear(self):
        for i in range(len(self._list)):
            self._list[i] = None, None
        self._len = 0

    def iteritems(self):
        for y in range(self._ymax):
            for x in range(self._xmax):
                isset, value = self._list[self._index((x,y))]
                if isset:
                    yield (x,y), value

    def __len__(self):
        return self._len


class Climate(object):
    breezedistance = 10
    
    def __init__(self, tiles, adjacency, cells, spin, tilt, profile = None):
        self.tiles = tiles
        self.adj = adjacency

        self.initdicts()

        self._season = None
        self.cells = cells
        self.spin = spin
        self.tilt = tilt

        if profile is not None:
            self._profile = profile
        else:
            class Profile(object):
                @staticmethod
                def runcall(f, *args, **kwargs):
                    f(*args, **kwargs)
            self._profile = Profile

    def initdicts(self):
        xmax = max([len(self.tiles[i]) for i in range(len(self.tiles))])

        dimensions = xmax, len(self.tiles)
        (self.direction,
         self.precipitation,
         self.convective,
         self.seabreeze,
         self.seabased,
         self.temperature,
         self.pressure) = [ClimateDict(dimensions) for i in range(7)]

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
                    h = self.tiles[y][x].elevation
                    t = (ins * (1 - h/10.0) if h > 0 else ins)
                    self.temperature[(x,y)] = t

                if convective:
                    p = (cos((self.tiles[y][x].lat*2*c + self.tilt*self.season)*pi/180) + 1)/2
                    self.convective[(x,y)] = p

                if pressure:
                    h = self.tiles[y][x].elevation
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

    def _seabreeze(self):
        if not self.seabreeze:
            frontier = []
            d = 0
            for y in range(len(self.tiles)):
                for x in range(len(self.tiles[y])):
                    if self.tiles[y][x].elevation <= 0:
                        self.seabreeze[(x,y)] = d
                        frontier.append((x,y))
                    else:
                        self.seabreeze[(x,y)] = None

            while d < self.breezedistance and frontier:
                d += 1
                frontier = self._propagate(frontier, d)

        d = self.breezedistance
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                breeze = self.seabreeze[(x,y)]
                if breeze is None:
                    h = 0
                else:
                    h = ((d - breeze)/float(d))**2
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
                if self.seabreeze[a] is None:
                    self.seabreeze[a] = d
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

    @property
    def tilemappings(self):
        return { 'params': (self.cells, self.spin),
                 'fwd_map': self._mapping,
                 'rev_map': self._destmap,
                 'wind_dir': self.direction,
                 'sorted_adj': self.sadj }

    @tilemappings.setter
    def tilemappings(self, value):
        if value['params'] != (self.cells, self.spin):
            raise ValueError('Params mismatch')

        self._mapping = value['fwd_map']
        self._destmap = value['rev_map']
        self.direction = value['wind_dir']
        self.sadj = value['sorted_adj']

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
                c[y][x] = (self.tiles[y][x].elevation,
                           self.temperature[(x,y)],
                           self.precipitation[(x,y)])

        return c
    
    def update(self):
        d, t, c, s, p = [not dic for dic in
                      self.direction, self.temperature, self.convective, self.seabased, self.pressure]
        if d or t or c or s or p:
            self._profile.runcall(self.resetclimate, d, t, c, s, p)

def climate(tiles, adjacency, seasons, cells, spin, tilt, temprange, tilemappings, profile = None):
    c = Climate(tiles, adjacency, cells, spin, tilt, profile)

    if tilemappings:
        c.tilemappings = tilemappings

    ss = []
    for s in seasons:
        c.season = s
        ss.append(c.average())

    if not tilemappings:
        tilemappings.update(c.tilemappings)
        
    seasons = []
    for y in range(len(ss[0])):
        row = []
        for x in range(len(ss[0][y])):
            row.append((ss[0][y][x][0],
                        [ss[i][y][x][1:] for i in range(len(ss))]))
        seasons.append(row)

    cc = ClimateClassification(seasons, temprange)
    cs = {}
    for y in range(len(tiles)):
        for x in range(len(tiles[y])):
            cs[(x,y)] = ClimateInfo(cc.climate[y][x][1], cc.climate[y][x][2], cc.climate[y][x][4])
    return cs
