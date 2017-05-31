from cPickle import dump, load

from climatemethod import ClimateInfo
from race import Heritage
from tile import Group, Layer, Tile

class Data(object):
    EXTENSION = '.tec9'

    @classmethod
    def loaddata(cls, data):
        if 'version' not in data or data['version'] < 9:
                raise ValueError('File version is too old')

        races, agricultural = cls._population(data['races'], data['agriculturalraces'], data['tiles'].iteritems())

        data['tiles'] = {v: cls._tile(t) for v,t in data['tiles'].iteritems()}

        data['shapes'] = [Group([data['tiles'][tv] for tv in tvs], v) for (tvs, v) in data['shapes']]

        data['population'] = {data['tiles'][v]: r for v, r in races.iteritems()}

        data['agricultural'] = agricultural

        return data

    @classmethod
    def load(cls, filename):
        with open(filename, 'r') as f:
            return cls.loaddata(load(f))

    @classmethod
    def savedata(cls, random, stage, dp, build, splitnum, tiles, shapes, glaciationtime, population, agricultural, hasatm, haslife):
        tileindex = cls._index(tiles)
        rs, rindex, ags = cls._raceagindices(population, agricultural)
        return {'version': 9,
                'random': random,
                'stage': stage,
                'dp': dp,
                'build': build,
                'splitnum': splitnum,
                'tiles': {v:
                           { 'lat': t.lat,
                             'lon': t.lon,
                             'substance': t.substance,
                             'climate': { 'temperature': t.climate.temperature,
                                          'precipitation': t.climate.precipitation,
                                          'koeppen': t.climate.koeppen,
                                          'life': t.climate.life }
                                        if t.climate is not None else None,
                             'race': rs.index(population[t]) if t in population else None }
                           for v,t in tiles.iteritems()},
                'shapes': [([tileindex[t.vector] for t in s.tiles], s.v) for s in shapes],
                'races': rindex,
                'agriculturalraces': ags,
                'glaciationtime': glaciationtime,
                'hasatm': hasatm,
                'haslife': haslife}

    @classmethod
    def save(cls, filename, data):
        if filename[-len(cls.EXTENSION):] != cls.EXTENSION:
            filename += cls.EXTENSION
        with open(filename, 'w') as f:
            dump(data, f, 0)

    @classmethod
    def _tile(cls, data):
        t = Tile(data['lat'], data['lon'])
        t.bottom = data['substance'][0]
        t.layers = [Layer(l['rock'], l['thickness']) for l in data['substance'][1]]
        t.limit()
        if data['climate'] is not None:
            t.climate = ClimateInfo(data['climate']['temperature'],
                                    data['climate']['precipitation'],
                                    data['climate']['koeppen'],
                                    data['climate']['life'])
        else:
            t.climate = None
        return t

    @classmethod
    def _index(cls, tiles):
        tileindex = {}
        for v,t in tiles.iteritems():
            tileindex[t.vector] = v
        return tileindex

    @classmethod
    def _raceagindices(cls, population, agricultural):
        def addh(h):
            hs = {h}
            if h.ancestry:
                for a in h.ancestry:
                    hs |= addh(a)
            return hs
        hset = set()
        for h in population.itervalues():
            hset |= addh(h)
        hs = list(hset)
        index = [({hs.index(a) for a in h.ancestry} if h.ancestry else set()) for h in hs]
        ags = [h in agricultural for h in hs]
        return hs, index, ags

    @classmethod
    def _population(cls, races, isagricultural, tiles):
        hs = []
        def reify(i, ais):
            while i > len(hs)-1:
                hs.append(None)
            if hs[i] is None:
                hs[i] = Heritage({reify(ai, races[ai]) for ai in ais}) if ais else Heritage()
            return hs[i]
        population = {}
        agricultural = set()
        for v, t in tiles:
            i = t['race']
            if i is not None:
                r = reify(i, races[i])
                if isagricultural[i]:
                    agricultural.add(r)
                population[v] = r
        return population, agricultural
