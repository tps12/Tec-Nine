from cPickle import dump, load

from climatemethod import ClimateInfo
from tile import Group, Layer, Tile

class Data(object):
    EXTENSION = '.tec9'

    @classmethod
    def load(cls, filename):
        with open(filename, 'r') as f:
            data = load(f)

            if 'version' not in data or data['version'] < 5:
                raise ValueError('File version is too old')

            if data['version'] < 6:
                for t in [t for lat in data['tiles'] for t in lat]:
                    t['climate']['temperature'] = 0

            data['tiles'] = [[cls._tile(t) for t in lat] for lat in data['tiles']]

            tileindex = cls._index(data['tiles'])

            data['shapes'] = [Group([tileindex[i] for i in tis], v) for (tis, v) in data['shapes']]

            return data

    @classmethod
    def save(cls, filename, random, dp, build, splitnum, tiles, shapes):
        if filename[-len(cls.EXTENSION):] != cls.EXTENSION:
            filename += cls.EXTENSION
        tileindex = cls._index(tiles)
        with open(filename, 'w') as f:
            dump({'version': 6,
                  'random': random,
                  'dp': dp,
                  'build': build,
                  'splitnum': splitnum,
                  'tiles': [[{ 'lat': t.lat,
                               'lon': t.lon,
                               'substance': t.substance,
                               'climate': { 'temperature': t.climate.temperature,
                                            'precipitation': t.climate.precipitation,
                                            'koeppen': t.climate.koeppen } }
                             for t in lat]
                            for lat in tiles],
                  'shapes': [([tileindex.index(t) for t in s.tiles], s.v) for s in shapes]},
                 f,
                 0)

    @classmethod
    def _tile(cls, data):
        t = Tile(data['lat'], data['lon'])
        t.bottom = data['substance'][0]
        t.layers = [Layer(l['rock'], l['thickness']) for l in data['substance'][1]]
        t.climate = ClimateInfo(data['climate']['temperature'],
                                data['climate']['precipitation'],
                                data['climate']['koeppen'])
        return t

    @classmethod
    def _index(cls, tiles):
        tileindex = []
        for lat in tiles:
            for t in lat:
                tileindex.append(t)
        return tileindex


