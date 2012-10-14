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

    def metamorphose(self):
        # accumulate depth from top down
        t = 0
        for i in range(len(self.layers)-1, -1, -1):
            t += self.layers[i].thickness
            dt = t - 5
            # beneath 5km, everything metamorphoses
            if dt >= 0:
                layers = self.layers
                # metamorphosed layers
                self.layers = [Layer(l.rock, l.thickness) for l in layers[:i]]
                # deep part of divided layer
                self.layers.append(Layer(layers[i].rock, dt))
                # metamorphose
                for l in self.layers:
                    try:
                        l.rock = l.rock.copy()
                        l.rock['type'] = 'M'
                        l.rock['name'] = 'M'
                    except AttributeError:
                        l.rock = { 'type': 'M', 'name': 'M' }
                # remaining piece of divided layer
                self.layers.append(Layer(layers[i].rock, layers[i].thickness - dt))
                # un-metamorphosed layers
                self.layers += layers[i+1:]
                break

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
        self.metamorphose()
        self.compact()

    def build(self, amount, rock):
        self.bottom -= amount
        self.layers.insert(0, Layer(rock, 2 * amount))
        self.limit()
        self.metamorphose()
        self.compact()

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

    @staticmethod
    def depositmaterials(materials):
        contributions = []
        depositkeys = set()
        for m in materials:
            t = 0
            i = len(m.substance[1]) - 1
            sources = []
            keys = set()
            while t < m.total:
                dt = m.total - t
                layer = m.substance[1][i]
                if layer['thickness'] >= dt:
                    sources.append({ 'rock': layer['rock'], 'thickness': dt })
                else:
                    sources.append(layer)
                keys = keys.union(sources[-1]['rock'].keys())
                t += sources[-1]['thickness']
                i -= 1

            rock = { 'type': 'S', 'name': 'S' }
            for k in keys:
                if k not in rock:
                    # weight attributes by thickness
                    rock[k] = sum([float(s['thickness']) * s['rock'][k]
                                   if k in s['rock'] else 0
                                   for s in sources])/m.total
            depositkeys = depositkeys.union(rock.keys())
            contributions.append({ 'rock': rock, 'thickness': m.amount })

        rock = { 'type': 'S', 'name': 'S' }
        thickness = sum([c['thickness'] for c in contributions])
        for k in depositkeys:
            if k not in rock:
                # weight attributes by thickness
                rock[k] = sum([float(c['thickness']) * c['rock'][k]
                               if k in c['rock'] else 0
                               for c in contributions])/thickness

        return Layer(rock, thickness)

    def depositnew(self, materials):
        if sum([m.amount for m in materials]) > 1.5:
            self.layers.append(self.depositmaterials(materials))
            self.metamorphose()
            self.compact()
            return True
        else:
            return False

    def depositexisting(self, materials):
        if len(materials) == 0:
            return
        self.layers.append(self.depositmaterials(materials))
        self.limit()
        self.metamorphose()
        self.compact()

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
