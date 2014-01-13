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
    def __init__(self, temperature, precipitation, koeppen, life):
        self.temperature = temperature
        self.precipitation = precipitation
        self.koeppen = koeppen
        self.life = life

def memoize(fn):
    c = {}
    def mf(*args):
        if not args in c:
            c[args] = fn(*args)
        return c[args]
    return mf

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
        (self.direction,
         self.precipitation,
         self.convective,
         self.seabreeze,
         self.seabased,
         self.sun,
         self.temperature,
         self.pressure) = [{} for _ in range(8)]

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

    @staticmethod
    def insolation(lat, season, tilt):
        theta = lat * pi/180
        theta += (tilt * pi/180) * season
        ins = max(0, cos(theta))
        return 0.5 + (ins - 0.5) * cos(tilt * pi/180)

    @staticmethod
    def winddirection(lat, c, s):
        n = abs(lat)/(90.0/c)
        n = int(n) & 1
        n = n if lat > 0 else not n
        d = 180 - 180 * n

        ce = 2 * s * sin(pi * (180-lat)/180.0)
        d += atan2(ce, 1) * 180/pi
        return d % 360

    def resetclimate(self, direction, temperature, convective, seabased, pressure):
        #res = max([len(r) for r in self.tiles]), len(self.tiles)
        c = self.cells

        e2 = 2 * exp(1)

        direction_fn = memoize(self.winddirection)
        insolation_fn = memoize(self.insolation)
        for v, tile in self.tiles.iteritems():
            if direction:
                self.direction[v] = direction_fn(tile.lat, c, self.spin)

            if temperature:
                self.sun[v] = ins = insolation_fn(tile.lat, self.season, self.tilt)
                h = tile.elevation
                t = (ins * (1 - h/10.0) if h > 0 else ins)
                self.temperature[v] = t

            if convective:
                p = (cos((tile.lat*2*c + self.tilt*self.season)*pi/180) + 1)/2
                self.convective[v] = p

            if pressure:
                h = tile.elevation
                if h > 0:
                    p = 0.5
                else:
                    p = 1-(cos((tile.lat*2*c + self.tilt*self.season)*pi/180) + 1)/2
                self.pressure[v] = p

            if direction or seabased:
                self.seabased[v] = None

        if direction:
            self.sadj = {}
            for v, ns in self.adj._adj.iteritems():
                c = tile.lat, tile.lon
                d = self.direction[v]
                self.sadj[v] = sorted(self.adj[v],
                                      key=lambda a: cos(
                                          (bearing(c,
                                                   (self.tiles[a].lat,
                                                    self.tiles[a].lon))
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
            for v, tile in self.tiles.iteritems():
                if tile.elevation <= 0:
                    self.seabreeze[v] = d
                    frontier.append(v)
                else:
                    self.seabreeze[v] = None

            while d < self.breezedistance and frontier:
                d += 1
                frontier = self._propagate(frontier, d)

        d = self.breezedistance
        for v in self.tiles:
            breeze = self.seabreeze[v]
            if breeze is None:
                h = 0
            else:
                h = ((d - breeze)/float(d))**2
            p = min(1.0, h + self.convective[v])
            self.seabased[v] = h

    def _totalprecipitation(self):
        d = self.breezedistance
        for v in self.tiles:
            p = min(1.0, self.seabased[v] + self.convective[v])
            self.precipitation[v] = p
                
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
        for v, tile in self.tiles.iteritems():
            nws = [(a, cos((bearing(
                (tile.lat, tile.lon),
                (self.tiles[a].lat, self.tiles[a].lon))
                    - self.direction[v])*pi/180))
                   for a in self.sadj[v]]
            nws = [nw for nw in nws if nw[1] > 0]

            for n, w in nws:
                addmap(v, n, w)
                seen.add(n)

        # map from sources for any tile that hasn't been targeted
        for v, tile in self.tiles.iteritems():
            if v not in seen:
                nws = [(a, -cos((bearing(
                    (tile.lat, tile.lon),
                    (self.tiles[a].lat, tile.lon))
                        - self.direction[a])*pi/180))
                       for a in self.sadj[v]]
                nws = [nw for nw in nws if nw[1] > 0]

                for n, w in nws:
                    addmap(n, v, w)

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
        c = {}
        for v, tile in self.tiles.iteritems():
            c[v] = (self.tiles[v].elevation,
                    self.temperature[v],
                    self.precipitation[v],
                    self.sun[v])

        return c
    
    def update(self):
        d, t, c, s, p = [not dic for dic in
                      self.direction, self.temperature, self.convective, self.seabased, self.pressure]
        if d or t or c or s or p:
            self._profile.runcall(self.resetclimate, d, t, c, s, p)

def climate(tiles, adjacency, seasons, cells, spin, tilt, temprange, life, tilemappings, profile = None):
    c = Climate(tiles, adjacency, cells, spin, tilt, profile)

    if tilemappings:
        c.tilemappings = tilemappings

    ss = []
    for s in seasons:
        c.season = s
        ss.append(c.average())

    if not tilemappings:
        tilemappings.update(c.tilemappings)
        
    seasons = {}
    for v in ss[0]:
        season = (ss[0][v][0], [ss[i][v][1:] for i in range(len(ss))])
        seasons[v] = season

    cc = ClimateClassification(seasons, temprange, life)
    cs = {}
    for v in tiles:
        cs[v] = { 'classification': ClimateInfo(cc.climate[v][1],
                                    cc.climate[v][2],
                                    cc.climate[v][4],
                                    cc.climate[v][5]),
                  'seasons': [{ 'temperature': s[0],
                                'precipitation': s[1],
                                'insolation': s[2] }
                              for s in seasons[v][1]] }
    return cs
