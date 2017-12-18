import disjoint

class ClimateParams(object):
    def __init__(self, temprange, preciprange, lightrange):
        self.temprange = temprange
        self.preciprange = preciprange
        self.lightrange = lightrange

    def inrange(self, season):
        for (k, r) in (('temperature', self.temprange),
                       ('precipitation', self.preciprange),
                       ('insolation', self.lightrange)):
            value = season[k]
            if value < r[0] or value > r[1]:
                return False
        return True

def mergeseasons(r, f, ss):
    if f in r:
        r[f] = sorted(list(set(r[f] + ss)))
    else:
        r[f] = ss

class Region(object):
    def __init__(self, fs):
        self.faces = fs

    def populateseasonalrange(self, r, default):
        for f in self.faces:
            mergeseasons(r, f, default)

class Seasonal(object):
    def __init__(self, r, ss):
        self.region = r
        self.seasons = ss

    def populateseasonalrange(self, r, _):
        self.region.populateseasonalrange(r, list(self.seasons))

# Composed of two Seasonal regions
class MigrationPattern(object):
    def __init__(self, r1, r2):
        self.first = r1
        self.second = r2

    def populateseasonalrange(self, r, _):
        self.first.populateseasonalrange(r, _)
        self.second.populateseasonalrange(r, _)

class Species(object):
    def __init__(self, name, biomesandmigrations):
        self.name = name
        self.habitats = biomesandmigrations

    def seasonalrange(self, numseasons):
        default = range(numseasons)
        r = {}
        for h in self.habitats:
            h.populateseasonalrange(r, default)
        return r

def findregions(tiles, adj, params):
    rs = {}
    for f, t in tiles.items():
        if t.elevation <= 0:
            continue
        for s in t.seasons:
            if not params.inrange(s):
                break
        else:
            rs[f] = disjoint.set()
            for n in adj[f]:
                if n in rs:
                    disjoint.union(rs[f], rs[n])
    regs = {}
    for f, s in rs.items():
        r = s.root()
        if r not in regs:
            regs[r] = set()
        regs[r].add(f)
    return [Region(fs) for fs in regs.values()]

def findseasonalregions(tiles, adj, params):
    rs = {}
    for f, t in tiles.items():
        if t.elevation <= 0:
            continue
        ss = tuple([i for i in range(len(t.seasons)) if params.inrange(t.seasons[i])])
        if not ss:
            continue
        k = (f, ss)
        rs[k] = disjoint.set()
        for n in adj[f]:
            nk = (n, ss)
            if nk in rs:
                disjoint.union(rs[k], rs[nk])
    regs = {}
    for k, s in rs.items():
        f, ss = k
        rk = (s.root(), ss)
        if rk not in regs:
            regs[rk] = set()
        regs[rk].add(f)
    return [Seasonal(Region(fs), ss) for ((_, ss), fs) in regs.items()]

# regions may be separated by water, up to caller to sort it out
def findmigratorypatterns(tiles, adj, params):
    for t in tiles.values():
        slen = len(t.seasons)
        break
    def gen():
        rs = findseasonalregions(tiles, adj, params)
        for r1 in rs:
            if len(r1.seasons) < slen:
                for r2 in rs:
                    if r2 is r1:
                        break
                    if len(r2.seasons) < slen:
                        if len(set(r1.seasons + r2.seasons)) == slen:
                            yield MigrationPattern(r1, r2)
    return [p for p in gen()]

def findhibernationregions(tiles, adj, params):
    toocold = max(0, min(0.3, params.temprange[0] - 0.01))
    winter = ClimateParams((toocold, params.temprange[0]), (0,1), (0,1))
    rs = {}
    for f, t in tiles.items():
        if t.elevation <= 0:
            continue
        ss = tuple([i for i in range(len(t.seasons)) if params.inrange(t.seasons[i])])
        if not ss or len(ss) == len(t.seasons):
            continue
        for i in range(len(t.seasons)):
            if i not in ss and not winter.inrange(t.seasons[i]):
                # winter is too cold
                break
        else:
            k = (f, ss)
            rs[k] = disjoint.set()
            for n in adj[f]:
                nk = (n, ss)
                if nk in rs:
                    disjoint.union(rs[k], rs[nk])
    regs = {}
    for k, s in rs.items():
        f, ss = k
        rk = (s.root(), ss)
        if rk not in regs:
            regs[rk] = set()
        regs[rk].add(f)
    return [Seasonal(Region(fs), ss) for ((_, ss), fs) in regs.items()]
