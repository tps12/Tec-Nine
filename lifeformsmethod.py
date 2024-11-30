import codecs
import json
import re
import time

import species

def populatefromparams(pop, name, params, tiles, adj, strats):
    for s in strats:
        habitats = s(tiles, adj, params)
        if habitats:
            pop.append(species.Species(name, habitats))
            break

range_pattern = re.compile('(-?[0-9]+)-(-?[0-9]+)')

def parse_range(s):
    m = range_pattern.match(s)
    return (float(m[1]), float(m[2]))

def normalize_temp(celsius_range):
    (low, high) = celsius_range
    return ((low + 25)/75, (high + 25)/75)

def normalize_precip(cm_range, num_seasons):
    (low, high) = cm_range
    # Rubber is a rainforest tree, should be close to 1
    # Desert < 0.1, temperate 0.5, monsoon close to 1
    # ~= 50         50-200         ~= 200+
    return (low/num_seasons/30, high/num_seasons/30)

def normalize_sun(hours_range, num_seasons):
    (low, high) = hours_range
    # Joshua tree is in the desert, should be close to 1
    return (low/num_seasons/400, high/num_seasons/400)

def plantparams(obj, num_seasons):
    return species.ClimateParams(
        normalize_temp(parse_range(obj['temperatureRange'])),
        normalize_precip(parse_range(obj['precipitationRange']), num_seasons),
        normalize_sun(parse_range(obj['sunlightRange']), num_seasons))

def animalparams(obj, num_seasons):
    return species.ClimateParams(
        normalize_temp(parse_range(obj['temperatureRange'])),
        normalize_precip(parse_range(obj['precipitationRange']), num_seasons),
        (0,1))

def settle(fauna, plants, tiles, adj, timing, limit=None, skip=0):
    start = time.time() if limit is not None else None
    attempted = 0
    logged = False
    num_seasons = len(next(iter(tiles.values())).seasons)
    for (name, pop, ranges_fn, strats) in [
            ('animals', fauna,
             animalparams,
             [species.findregions, species.findhibernationregions, species.findmigratorypatterns]),
            ('plants', plants,
             plantparams,
             [species.findseasonalregions])]:
        with codecs.open('{}.tsv'.format(name), 'r', 'utf-8') as f:
            for line in f.readlines():
                (species_name, data) = [s.strip() for s in line.split('\t')]
                if attempted >= skip:
                    if not logged:
                        timing.start('settling {}'.format(name))
                        logged = True
                    populatefromparams(pop, species_name, ranges_fn(json.loads(data), num_seasons), tiles, adj, strats)
                    skip += 1
                attempted += 1
                if start and time.time() - start > limit:
                    return skip
    return None
