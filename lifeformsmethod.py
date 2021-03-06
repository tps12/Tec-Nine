import codecs
import random
import time

import species

def populatefromparams(pop, name, params, tiles, adj, strats):
    for s in strats:
        habitats = s(tiles, adj, params)
        if habitats:
            pop.append(species.Species(name, habitats))
            break

def randomparams(temprange, preciprange, lightrange):
    return species.ClimateParams(
        tuple(sorted([random.gauss(*temprange[0]), random.gauss(*temprange[1])])),
        tuple(sorted([random.gauss(*preciprange[0]), random.gauss(*preciprange[1])])),
        tuple(sorted([random.gauss(*lightrange[0]), random.gauss(*lightrange[1])])))

def settle(fauna, plants, trees, tiles, adj, timing, limit=None, skip=0):
    start = time.time() if limit is not None else None
    attempted = 0
    logged = False
    for (name, pop, ranges, strats) in [
            ('animals', fauna,
             (((.4,.1), (.6,.1)), ((.25,.1), (.95,.1)), ((.1,.1), (.95,.1))),
             [species.findregions, species.findhibernationregions, species.findmigratorypatterns]),
            ('plants', plants,
             (((.2,.1), (.95,.1)), ((.4,.2), (.95,.1)), ((.4,.2), (.95,.1))),
             [species.findseasonalregions]),
            ('trees', trees,
             (((.2,.1), (.95,.1)), ((.5,.1), (.95,.1)), ((.5,.1), (.95,.1))),
             [species.findseasonalregions])]:
        with codecs.open('{}.txt'.format(name), 'r', 'utf-8') as f:
            for line in f.readlines():
                if attempted >= skip:
                    if not logged:
                        timing.start('settling {}'.format(name))
                        logged = True
                    populatefromparams(pop, line.strip(), randomparams(*ranges), tiles, adj, strats)
                    skip += 1
                attempted += 1
                if start and time.time() - start > limit:
                    return skip
    return None
