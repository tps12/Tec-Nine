from math import sin, cos, pi, atan2, sqrt

class Layer(object):
    def __init__(self, rock, thickness):
        self.rock = rock
        self.thickness = thickness

    def __eq__(self, other):
        return self.rock == other.rock and self.thickness == other.thickness

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'Layer({0}, {1})'.format(repr(self.rock), repr(self.thickness))

class Group(object):
    def __init__(self, tiles, v):
        self.tiles = tiles
        self.v = v

class Tile(object):
    MAX_HEIGHT = 10
    MAX_THICKNESS = 75

    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

        cos_lat = cos(self.lat * pi/180)
        self.vector = (cos_lat * cos(self.lon * pi/180),
                       cos_lat * sin(self.lon * pi/180),
                       sin(self.lat * pi/180))

        self.emptyocean()
        self._subduction = 0
        self._intrusion = None

    @property
    def subduction(self):
        return self._subduction

    @property
    def intrusion(self):
        return self._intrusion

    @property
    def substance(self):
        return self.bottom, [{ 'rock': l.rock, 'thickness': l.thickness } for l in self.layers]

    def distance(self, other):
        lat1, lon1 = [c * pi/180 for c in self.lat, self.lon]
        lat2, lon2 = [c * pi/180 for c in other.lat, other.lon]

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        return 2 * atan2(sqrt(a), sqrt(1-a))

    def limit(self):
        shrunk = 0
        while self.thickness > self.MAX_THICKNESS:
            dt = self.thickness - self.MAX_THICKNESS
            l = self.layers.pop(0)
            dlt = min(dt, l.thickness)
            if dlt < l.thickness:
                self.layers.insert(0, Layer(l.rock, l.thickness - dlt))
            shrunk += dlt

        self.bottom += shrunk

        de = self.elevation - self.MAX_HEIGHT
        if de > 0:
            self.bottom -= de

    def transform(self, layers):
        self.layers = [Layer(l['rock'], l['thickness']) for l in layers]
        self.compact()

    def compact(self):
        """Merge adjacent identical layers."""
        i = 0
        while i < len(self.layers) - 1:
            l = self.layers[i]
            if l.rock == self.layers[i+1].rock:
                self.layers[i] = Layer(l.rock, l.thickness + self.layers.pop(i+1).thickness)
            else:
                i += 1

    @staticmethod
    def mergelayers(sources):
        # each source is a (bottom, substance-list) tuple; convert substance list to layers
        sources = [(s[0], [Layer(l['rock'], l['thickness']) for l in s[1]]) for s in sources]

        # general approach is:
        #  - work from the highest elevation down
        #  - at each layer transition in any source:
        #     - among the sources with something defined at that level
        #         - choose the most common one
        #     - if there is more than one possibility for most common
        #         - choose one that differs from the previous (above) level
        #     - if the layer matches the previous one, extend it

        # pad source bottoms with empty layers
        bottom = min([s[0] for s in sources])
        ss = []
        for s in sources:
            db = s[0] - bottom
            pl = [Layer(None, db)] if db > 0 else []
            ss.append(pl + s[1])

        # pad source tops with empty layers
        elevation = max([s[0] + sum([l.thickness for l in s[1]]) for s in sources])
        for i in range(len(sources)):
            de = elevation - (sources[i][0] + sum([l.thickness for l in sources[i][1]]))
            if de > 0:
                ss[i].append(Layer(None, de))

        output = []
        depth = 0

        lastr = None
        
        # while there's anything left to work with
        while any([len(s) for s in ss]):
            # grab the next smallest layer down
            i = min(range(len(ss)), key=lambda i: ss[i][-1].thickness if len(ss[i]) > 0 else float('inf'))

            # take the rocks from the other sources, shrinking their layers
            t = ss[i][-1].thickness
            rs = []
            for s in ss:
                if len(s) == 0:
                    continue
                l = s.pop()
                if l.thickness > t:
                    s.append(Layer(l.rock, l.thickness - t))
                if l.rock is not None:
                    for ri in range(len(rs)):
                        if rs[ri][0] == l.rock:
                            rs[ri][1] += 1
                            break
                    else:
                        rs.append([l.rock, 1])

            if len(rs) == 0:
                continue

            # vote
            v = max([r[1] for r in rs])
            rs = [r[0] for r in rs if r[1] == v]

            # prefer unique
            if len(rs) > 1 and lastr in rs:
                rs.remove(lastr)

            if len(rs) > 0:
                lastr = rs[0]
                output.append(Layer(lastr, t))
        
        # compact
        i = 0
        while i < len(output)-1:
            t, n = output[i:i+2]
            if t.thickness == 0:
                output[i:i+2] = [n]
            else:
                if t.rock == n.rock:
                    output[i:i+2] = [Layer(t.rock, t.thickness + n.thickness)]
                else:
                    i += 1

        # reverse
        return bottom, list(reversed(output))

    def mergesources(self, groups):
        # average out each group
        gs = [self.mergelayers(ss) for ss in groups]
        # stack the groups up (in arbitrary order!)
        self.bottom = sum([g[0] for g in gs])
        self.layers = [s for ss in [g[1] for g in gs] for s in ss]
        self.limit()
        self.compact()

    def build(self, amount, rock):
        self.bottom -= amount
        self.layers.insert(0, Layer(rock, 2 * amount))
        self.limit()
        self.compact()
        self._subduction = amount

    def erode(self, erosion):
        e = erosion[self]
        m = sum([d.degree for d in e.destinations])
        for d in e.destinations:
            erosion[d.destination].addmaterial(d.degree, m, self.substance)
        while m > 0:
            l = self.layers.pop()
            if l.thickness > m:
                self.layers.append(Layer(l.rock, l.thickness - m))
                m = 0
            else:
                m -= l.thickness
        self.compact()

    def deposit(self, substance):
        self.layers.append(Layer(substance['rock'], substance['thickness']))
        self.limit()
        self.compact()

    def isostasize(self, amount):
        self.bottom += amount
        self.limit()

    def intrude(self, rock):
        # more mafic intrusions don't get as high
        depth = max(2, self.thickness * (1 - rock['felsity']))
        l = len(self.layers) - 1
        d = 0
        while d < depth and l >= 0:
            d += self.layers[l].thickness
            l -= 1
        intrusion = Layer(rock, 1)
        self.layers[l:l] = [intrusion]
        self.bottom -= intrusion.thickness
        self.limit()
        self.compact()
        self._intrusion = d, d + intrusion.thickness

    def cleartemp(self):
        self._subduction = 0
        self._intrusion = None

    def emptyland(self, rock = 'I', h = 1):
        self.bottom = -9
        self.layers = [Layer(rock, 9 + h)]

    def emptyocean(self, rock = 'I'):
        self.bottom = -5
        self.layers = [Layer(rock, 5)]

    @property
    def elevation(self):
        return max(0, self.bottom + self.thickness)

    @property
    def thickness(self):
        return sum([l.thickness for l in self.layers])

    def __repr__(self):
        return 'Tile({0}, {1})'.format(self.lat, self.lon)
