from pickle import dump, load

from climatemethod import ClimateInfo
from race import Heritage
from tile import Group, Layer, Tile

class Data(object):
    EXTENSION = '.tec9'

    @classmethod
    def loaddata(cls, data):
        if 'version' not in data or data['version'] < 25:
                raise ValueError('File version is too old')

        races, agricultural = cls._population(data['races'], data['racenames'], data['agriculturalraces'], data['tiles'].items())

        data['tiles'] = {v: cls._tile(t) for v,t in data['tiles'].items()}

        data['shapes'] = [Group([data['tiles'][tv] for tv in tvs], v) for (tvs, v) in data['shapes']]

        data['population'] = {data['tiles'][v]: r for v, r in races.items()}

        data['agricultural'] = agricultural

        return data

    @classmethod
    def load(cls, filename):
        with open(filename, 'rb') as f:
            return cls.loaddata(load(f))

    @classmethod
    def savedata(cls, random, gridsize, stage, spin, cells, tilt, dp, build, splitnum, tiles, shapes, glaciationtime, population, agricultural, atmt, lifet, historyinited, species, terraincap, terrainpop, statecolors, boundaries, tilespecies, languages, statespecies):
        tileindex = cls._index(tiles)
        rs, rnames, rindex, ags = cls._raceagindices(population, agricultural)
        return {'version': 25,
                'random': random,
                'gridsize': gridsize,
                'stage': stage,
                'spin': spin,
                'cells': cells,
                'tilt': tilt,
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
                             'seasons': t.seasons if t.seasons is not None else None,
                             'race': rs.index(population[t]) if t in population else None }
                           for v,t in tiles.items()},
                'shapes': [([tileindex[t.vector] for t in s.tiles], s.v) for s in shapes],
                'races': rindex,
                'racenames': rnames,
                'agriculturalraces': ags,
                'glaciationtime': glaciationtime,
                'hasatm': atmt == 0,
                'haslife': lifet == 0,
                'atmt': atmt,
                'lifet': lifet,
                'historyinited': historyinited,
                'species': species if historyinited else [],
                'terraincap': terraincap if historyinited else {},
                'terrainpop': terrainpop if historyinited else {},
                'nationcolors': statecolors if historyinited else [],
                'boundaries': boundaries if historyinited else {},
                'tilespecies': tilespecies if historyinited else {},
                'languages': languages if historyinited else [],
                'statespecies': statespecies if historyinited else []}

    @classmethod
    def save(cls, filename, data):
        if filename[-len(cls.EXTENSION):] != cls.EXTENSION:
            filename += cls.EXTENSION
        with open(filename, 'wb') as f:
            dump(data, f, 0)

    @classmethod
    def _tile(cls, data):
        t = Tile(data['lat'], data['lon'])
        t.bottom = data['substance'][0]
        t._mountainosity = data['substance'][1]
        t.layers = [Layer(l['rock'], l['thickness']) for l in data['substance'][-1]]
        t.limit()
        if data['climate'] is not None:
            t.climate = ClimateInfo(data['climate']['temperature'],
                                    data['climate']['precipitation'],
                                    data['climate']['koeppen'],
                                    data['climate']['life'])
        else:
            t.climate = None
        t.seasons = data['seasons'] if data['seasons'] is not None else None
        return t

    @classmethod
    def _index(cls, tiles):
        tileindex = {}
        for v,t in tiles.items():
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
        for h in population.values():
            hset |= addh(h)
        hs = list(hset)
        names = [h.name for h in hs]
        index = [({hs.index(a) for a in h.ancestry} if h.ancestry else set()) for h in hs]
        ags = [h in agricultural for h in hs]
        return hs, names, index, ags

    @classmethod
    def _population(cls, races, names, isagricultural, tiles):
        hs = []
        def reify(i, ais):
            while i > len(hs)-1:
                hs.append(None)
            if hs[i] is None:
                hs[i] = Heritage(names[i], {reify(ai, races[ai]) for ai in ais} if ais else None)
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
