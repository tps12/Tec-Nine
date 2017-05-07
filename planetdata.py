from cPickle import dump, load

from climatemethod import ClimateInfo
from tile import Group, Layer, Tile

class Data(object):
    EXTENSION = '.tec9'

    @classmethod
    def load(cls, filename):
        with open(filename, 'r') as f:
            data = load(f)

            if 'version' not in data or data['version'] < 7:
                raise ValueError('File version is too old')

            data['tiles'] = {v: cls._tile(t) for v,t in data['tiles'].iteritems()}

            data['shapes'] = [Group([data['tiles'][tv] for tv in tvs], v) for (tvs, v) in data['shapes']]

            return data

    @classmethod
    def save(cls, filename, random, dp, build, splitnum, tiles, shapes):
        if filename[-len(cls.EXTENSION):] != cls.EXTENSION:
            filename += cls.EXTENSION
        tileindex = cls._index(tiles)
        with open(filename, 'w') as f:
            dump({'version': 7,
                  'random': random,
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
                                          if t.climate is not None else None }
                             for v,t in tiles.iteritems()},
                  'shapes': [([tileindex[t.vector] for t in s.tiles], s.v) for s in shapes]},
                 f,
                 0)

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


