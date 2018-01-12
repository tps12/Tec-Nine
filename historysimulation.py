import math
import random
import statistics
import time

from dist2 import dist2
from grid import Grid
from hexadjacency import Adjacency
import language.dictionary
from language.lexicon import lexicon
import language.output
from language.phonemes import phonemes
import language.stats
import languagesimulation
import lifeformsmethod
from planetdata import Data
from pointtree import PointTree
import populationlevel
import populationmethod
import riversmethod
from prehistorysimulation import PrehistorySimulation
from rock import igneous
from terrainmethod import terrain, elevation, routerivers
from tile import *
from timing import Timing

class Population(object):
    def __init__(self, heritage, thousands):
        self.heritage = heritage
        self.thousands = thousands

minspecies = 20

class HistorySimulation(object):
    coastprox = PrehistorySimulation.coastprox
    minriverelev = PrehistorySimulation.minriverelev
    minriverprecip = PrehistorySimulation.minriverprecip
    seasons = PrehistorySimulation.seasons

    _timing = Timing()

    def __init__(self, gridsize, pauseafterinit):
        initt = self._timing.routine('simulation setup')

        initt.start('building grid')

        self._initgrid(gridsize)

        self.tiles = {}
        for v in self._grid.faces:
            x, y, z = v
            lat = 180/pi * atan2(z, sqrt(x*x + y*y))
            lon = 180/pi * atan2(y, x)
            self.tiles[v] = Tile(lat, lon)

        for t in self.tiles.values():
            t.emptyocean(self.seafloor())
            t.climate = t.seasons = None
            t.candidate = False

        self._terrain = terrain(self.grid, self.tiles)
        self._terrainadj = Adjacency(self._terrain)
        self.terrainchanged = False
        self._elevation = {f: elevation(f, self._terrain, self.tiles) for f in self._terrain.faces}
        self.populated = {}
        self.agricultural = set()

        initt.start('building indexes')
        self.shapes = []
        self.adj = Adjacency(self._grid)
        self._glaciationt = 0
        self.initindexes()

        self.phase = 'uninit'
        self._species = []
        self._capacity = {}
        self._population = {}
        self.nationcolors = []
        self.boundaries = {}
        self._tilespecies = {}
        self._nationspecies = {}
        self._nationlangs = []
        self._inited = False
        self._initingnations = None

        self._tradepartners = set()

        self._pauseafterinit = pauseafterinit

        initt.done()

    def _initgrid(self, gridsize):
        grid = Grid()
        while grid.size < gridsize:
            grid = Grid(grid)
            grid.populate()
        self._grid = grid

    def initindexes(self):
        self._indexedtiles = []
        for t in self.tiles.values():
            self._indexedtiles.append(t)

        self._tileadj = dict()
        for v in self._grid.faces:
            self._tileadj[self.tiles[v]] = set([self.tiles[nv] for nv in self.adj[v]])

        self._index = PointTree(dict([[self._indexedtiles[i].vector, i]
                                      for i in range(len(self._indexedtiles))]))

    def nearest(self, loc):
        return self._indexedtiles[self._index.nearest(loc)[0]]

    @property
    def initialized(self):
        return self._inited

    def initnations(self):
        timing = yield
        self.phase = 'species'
        settle = self.settlespecies(self.tiles, self.adj)
        next(settle)
        settle.send(timing)
        while True:
            try:
                timing = yield
                self._species = settle.send(timing)
                self._tilespecies = self.tilespecies(self._species, self.seasons)
            except StopIteration:
                break
        self.phase = 'nations'
        timing.start('determining carrying capacities')
        self._capacity = self.capacity(self.grid, self.tiles, self._terrain, self._tileadj, self.rivers)
        timing.start('determining population')
        self._population = self.population(self.grid, self.tiles, self._terrain, self.populated, self.agricultural)
        timing.start('creating national boundaries')
        for _ in self.nationalboundaries(self.nationcolors, self.boundaries,
                                         self._terrain, self._elevation, self.riverroutes, self._terrainadj, self.tiles,
                                         self._population, self.agricultural):
            timing = yield
            timing.start('continuing national boundaries')
        timing = yield
        self.phase = 'langs'
        start = time.time()
        timing.start('finding populations by location')
        self._tilespecies = self.tilespecies(self._species, self.seasons)
        timing.start('bucketing life by nation')
        self._nationspecies = self.nationspecies(self.boundaries, self._terrain, self._tilespecies)
        self.boundaries = {f: i for (f,i) in self.boundaries.items() if len(self._nationspecies[i]) >= minspecies}
        self._population = {f: (ps if f in self.boundaries else []) for (f,ps) in self._population.items()}
        timing.start('naming species')
        for lang in self.langfromspecies(self._nationspecies):
            self._nationlangs.append(lang)
            if time.time() - start > 5:
                timing = yield
                timing.start('continuing naming species')
                start = time.time()

        # to fill in coast at terrain scale
        self.phase = 'coasts'
        for _ in range(2):
            timing = yield
            timing.start('populating coasts')
            self.grow(timing)
        self.phase = 'sim'

    def keepiniting(self):
        if not self._initingnations:
            timing = self._timing.routine('initializing history')
            self._initingnations = self.initnations()
            next(self._initingnations)
        else:
            timing = self._timing.routine('continuing initialization')

        try:
            self._initingnations.send(timing)
        except StopIteration:
            self._initingnations = None
            self._inited = True
        timing.done()

    def grow(self, stept):
        stept.start('growing populations')
        grow = lambda p0, K: K/(1 + (K-p0)/p0 * math.exp(-0.25)) # k=0.25 pretty arbitrary, aiming for 1% yearly growth
        deltas = {}
        for f, ps in self._population.items():
            for p in ps:
                neighborhood = [f] + [n for n in self._terrainadj[f] if n in self._elevation and self._elevation[n]]
                nations = {self.boundaries[f]} if f in self.boundaries else {self.boundaries[n] for n in self._terrainadj[f]}
                capacities = [self._capacity[n][1 if p.heritage in self.agricultural else 0] for n in neighborhood]
                pops = [sum([np.thousands for np in self._population[n]]) for n in neighborhood]
                K = max(0, sum(capacities) - sum(pops)) + capacities[0]
                delta = grow(p.thousands, K) - p.thousands if K > 0 else 0
                if delta < 0:
                    continue
                spaces = [(sum(pops) - pop)/float(sum(pops)) for pop in pops]
                for i in range(len(spaces)):
                    if spaces[i] > 0:
                        share = delta * spaces[i]
                        n = neighborhood[i]
                        if n not in deltas:
                            deltas[n] = ([], set())
                        for dp in deltas[n][0]:
                            if dp.heritage is p.heritage:
                                dp.thousands += share
                                break
                        else:
                            deltas[n][0].append(Population(p.heritage, share))
                        deltas[n][1].update(nations)

        stept.start('assigning growth values')
        frontierspecies = {}
        for f, (dps, nations) in deltas.items():
            if f not in self._population:
                self._population[f] = []
            ps = self._population[f]
            for dp in dps:
                for p in ps:
                    if p.heritage is dp.heritage:
                        p.thousands += dp.thousands
                        break
                else:
                    ps.append(dp)
            if f not in self.boundaries:
                i = random.choice(list(nations))
                self.boundaries[f] = i
                if i not in frontierspecies:
                    frontierspecies[i] = set()

        stept.start('getting species in expanded national boundaries')
        for f in deltas:
            nation_index = self.boundaries[f]
            if nation_index in frontierspecies:
                frontierspecies[nation_index] |= self.facespecies(f, self._terrain, self._tilespecies)

        stept.start('naming new species')
        for nation_index, species_indices in frontierspecies.items():
            dictionary = self._nationlangs[nation_index]
            species = self._nationspecies[nation_index]
            for species_index in species_indices:
                if not dictionary.describes('species', species_index):
                    species.append(species_index)
            existing_names = set(dictionary.lexicon())
            lang = language.stats.Language(existing_names)
            new_species = species[len(existing_names):]
            new_names = list(lexicon(list(lang.vowels), list(lang.consonants), lang.stress, lang.onsetp, lang.codap, lang.constraints, len(new_species), existing_names))
            random.shuffle(new_names)
            for j in range(len(new_species)):
                dictionary.add(new_names[j], 'species', new_species[j])

        stept.start('removing empty populations')
        for ps in self._population.values():
            for i in [i for i in reversed(range(len(ps))) if not ps[i].thousands]:
                del ps[i]

    @staticmethod
    def nationalextents(boundaries):
        extents = []
        for f, n in boundaries.items():
            while n > len(extents)-1:
                extents.append(set())
            extents[n].add(f)
        return extents

    @staticmethod
    def riverneighbors(f, terrainadj, rivers):
        ns = terrainadj[f]
        res = set(ns)
        for g in ns:
            for r in rivers:
                if g in r:
                    res |= terrainadj[g]
                break
        return res

    @staticmethod
    def neighboringnations(extents, terrainadj, rivers, boundaries):
        neighbors = [set() for _ in extents]
        for n in range(len(extents)):
            for f in extents[n]:
                neighbors[n] |= {boundaries[g] for g in HistorySimulation.riverneighbors(f, terrainadj, rivers) if g in boundaries} - {n}
        return neighbors

    @staticmethod
    def tradepressure(neighbors, nationspecies, partners):
        pressure = [{} for _ in neighbors]
        for n in range(len(neighbors)):
            native = set(nationspecies[n])
            for o in neighbors[n]:
                ospecies = set(nationspecies[o])
                for partner in HistorySimulation.recursivetradepartners(o, partners, {}):
                    if partner != n:
                        ospecies |= set(nationspecies[partner])
                p = len(ospecies - native)
                if p > 0:
                    pressure[n][o] = p
        return pressure

    @staticmethod
    def tradingeligibility(pressure, nationspecies, threshold):
        return [{o for (o, p) in pressure[n].items() if p >= len(nationspecies[n]) * threshold}
                for n in range(len(pressure))]

    @staticmethod
    def mutualpartners(eligible):
        return [{o for o in eligible[n] if n in eligible[o]}
                for n in range(len(eligible))]

    @staticmethod
    def tradepartners(mutual, pressure):
        return {tuple(sorted((n, o))) for n in range(len(mutual)) for o in mutual[n]}

    def facehighlighted(self, f):
        if f in self.boundaries:
            n = self.boundaries[f]
            for g in self.riverneighbors(f, self._terrainadj, self.riverroutes):
                if g in self.boundaries:
                    o = self.boundaries[g]
                    if o != n and tuple(sorted([n, o])) in self._tradepartners:
                        return True
        return False

    @staticmethod
    def lookuptradepartners(n, partners):
        return {o for (o, p) in partners if p == n} | {p for (o, p) in partners if o == n}

    @staticmethod
    def recursivetradepartners(n, partners, memo, seen=None):
        seen = seen if seen is not None else set()
        if n in memo:
            return memo[n]
        if n in seen:
            return set()
        os = HistorySimulation.lookuptradepartners(n, partners)
        for o in sorted(list(os)):
            os |= HistorySimulation.recursivetradepartners(o, partners, memo, seen | {n})
        memo[n] = os
        return os

    def nationtradepartners(self, n):
        return self.lookuptradepartners(n, self._tradepartners)

    @staticmethod
    def borrow(word, lang, stats):
        for adapted in languagesimulation.adaptsounds(word, stats.vowels, stats.consonants, stats.stress):
            for borrowed in languagesimulation.constrain(adapted, stats.constraints, stats.vowels, stats.stress):
                if not lang.defines(borrowed):
                    return borrowed
        # nothing unique yet, try adding a new suffix
        for adapted in languagesimulation.adaptsounds(word, stats.vowels, stats.consonants, stats.stress):
            for borrowed in languagesimulation.constrain(adapted, stats.constraints, stats.vowels, stats.stress):
                borrowed = language.words.Word(
                    borrowed.syllables +
                        lexicon(list(stats.vowels), list(stats.consonants), 0, stats.onsetp, stats.codap, stats.constraints, 1).pop().syllables,
                    stats.stress)
                if not lang.defines(borrowed):
                    return borrowed
        raise Exception("Couldn't borrow {}".format(word))

    @staticmethod
    def borrowfrom(resource, langs, stats, src, dest, tradepartners, seen=None):
        seen = seen if seen is not None else {dest}
        if langs[dest].describes(*resource):
            return True
        if not langs[src].describes(*resource):
            for partner in HistorySimulation.lookuptradepartners(src, tradepartners):
                if partner in seen:
                    continue
                if HistorySimulation.borrowfrom(resource, langs, stats, partner, src, tradepartners, seen | {src}):
                    break
            else:
                return False
        langs[dest].add(HistorySimulation.borrow(langs[src].describe(*resource), langs[dest], stats[dest]), *resource)
        return True

    def update(self):
        if not self._inited:
            self.keepiniting()
            return self._inited and self._pauseafterinit

        stept = self._timing.routine('simulation step')

        stept.start('making sound changes')
        for dictionary in self._nationlangs:
            if dictionary is None:
                continue
            changes = {}
            for name in sorted(dictionary.lexicon(), key=language.output.pronounce):
                newname = random.choice(languagesimulation.soundchanges)(name)
                if name != newname and not dictionary.defines(newname) and newname not in changes:
                    changes[newname] = name
            for (newname, name) in changes.items():
                dictionary.rename(name, newname)

        self.grow(stept)

        stept.start('finding extents of nations')
        extents = self.nationalextents(self.boundaries)
        stept.start('identifying neighbors')
        neighbors = self.neighboringnations(extents, self._terrainadj, self.riverroutes, self.boundaries)
        stept.start('determining trade benefit for neighbors')
        pressure = self.tradepressure(neighbors, self._nationspecies, self._tradepartners)
        stept.start('finding eligible trade partners')
        eligible = self.tradingeligibility(pressure, self._nationspecies, 0.05)
        stept.start('identifying mutually eligible partners')
        mutual = self.mutualpartners(eligible)
        stept.start('establishing trade relationships')
        self._tradepartners |= self.tradepartners(mutual, pressure)

        stept.start('loaning words')
        stats = [language.stats.Language(lang.lexicon()) if lang is not None else None for lang in self._nationlangs]
        for n in range(len(self.nationcolors)):
            lang = None
            partners = self.nationtradepartners(n)
            for partner in partners:
                if lang is None:
                    lang = self._nationlangs[n]
                if not lang.describes('nation', partner):
                    lang.add(HistorySimulation.borrow(self._nationlangs[partner].describe('nation', partner), lang, stats[n]), 'nation', partner)
            for resource in self.imports(n):
                if lang.describes(*resource):
                    continue
                for partner in partners:
                    if self.borrowfrom(resource, self._nationlangs, stats, partner, n, self._tradepartners):
                        break

        stept.done()

    @property
    def grid(self):
        return self._grid

    @property
    def faces(self):
        faces = {}
        grid = self._terrain
        while True:
            for f, vs in grid.faces.items():
                if f not in faces:
                    faces[f] = vs
            if grid == self._grid:
               break
            grid = grid.prev
        return faces

    @staticmethod
    def seafloor():
        return igneous.extrusive(0.5)

    @staticmethod
    def settlespecies(tiles, adj):
        fauna, plants, trees = [], [], []
        timing = yield
        skip = 0
        while True:
           skip = lifeformsmethod.settle(fauna, plants, trees, tiles, adj, timing, 5, skip)
           timing = yield fauna + plants + trees
           if skip is None:
               break

    def faceelevation(self, f):
        return self._elevation[f] if f in self._elevation else 0

    def facecapacity(self, f):
        return (self._capacity[f][1 if any([p.heritage in self.agricultural for p in self._population[f]]) else 0]
                if f in self._capacity and f in self._population else 0)

    def facepopulation(self, f):
        return sum([p.thousands for p in self._population[f]]) if f in self._population else 0

    @classmethod
    def paleocapacity(cls, t, adj, rivers):
        if populationmethod.squattable(t, adj, cls.coastprox, rivers):
            return populationlevel.paleolithic(t.climate.koeppen)
        return 0

    @classmethod
    def agracapacity(cls, t, _, _2):
        if populationmethod.farmable(t):
            return populationlevel.withagriculture(t.climate.koeppen)
        return 0

    @classmethod
    def capacity(cls, grid, tiles, terrain, adj, rivers):
        capacity = {}
        coast = set()
        for f in terrain.faces:
            if f in grid.vertices:
                # face is a vertex of the coarse grid, gets average of three elevated faces
                pfs = [pf for pf in grid.vertices[f] if tiles[pf].elevation]
                capacity[f] = tuple([sum([fn(tiles[pf], adj, rivers) for pf in pfs])/(9.0 * len(pfs))
                                     for fn in (cls.paleocapacity, cls.agracapacity)])
            else:
                # fully contained by coarse face
                if f in grid.faces:
                    t = tiles[f]
                else:
                    # edge face, is a vertex of parent grid, between three faces, exactly one of which
                    # is also in the coarse grid
                    t = tiles[[pf for pf in terrain.prev.vertices[f] if pf in grid.faces][0]]
                    if not t.elevation:
                        # parent is underwater, leave it for later
                        coast.add(f)
                        continue
                capacity[f] = tuple([fn(t, adj, rivers)/9.0
                                     for fn in (cls.paleocapacity, cls.agracapacity)])

        # now fill in the coastal tiles we skipped with the average values of their neighbors
        tadj = Adjacency(terrain)
        for f in coast:
            ns = [n for n in tadj[f] if n in capacity and capacity[n] != (0, 0)]
            capacity[f] = tuple([sum([capacity[n][i] for n in ns])/float(len(ns)) for i in range(2)]) if len(ns) else (0, 0)

        return capacity

    @staticmethod
    def population(grid, tiles, terrain, populated, agricultural):
        population = {}
        for f in terrain.faces:
            population[f] = []
            if f in grid.vertices:
                # face is a vertex of the coarse grid, gets 1/3 of a share (1/27) from each of three coarse faces
                for t in [tiles[pf] for pf in grid.vertices[f]]:
                    if t in populated:
                        r = populated[t]
                        n = populationlevel.count(t, r, agricultural)/27.0
                        ps = population[f]
                        for p in ps:
                            if p.heritage is r:
                                p.thousands += n
                                break
                        else:
                            ps.append(Population(r, n))
            else:
                # fully contained by coarse face, gets a full share (1/9) of population
                if f in grid.faces:
                    t = tiles[f]
                else:
                    # edge face, is a vertex of parent grid, between three faces, exactly one of which
                    # is also in the coarse grid
                    t = tiles[[pf for pf in terrain.prev.vertices[f] if pf in grid.faces][0]]
                if t in populated:
                    r = populated[t]
                    n = populationlevel.count(t, r, agricultural)/9.0
                    ps = population[f]
                    for p in ps:
                        if p.heritage is r:
                            p.thousands += n
                            break
                    else:
                        ps.append(Population(r, n))
        return population

    @staticmethod
    def hasagriculture(f, population, agricultural):
        return f in population and any([p.heritage in agricultural for p in population[f]])

    @staticmethod
    def cityprob(f, terrain, tiles, population, agricultural):
        coarse = terrain.prev.prev
        if f in coarse.vertices:
            # face is a vertex of the coarse grid, get mode climate if there is one
            ks = [tiles[pf].climate.koeppen for pf in coarse.vertices[f]]
            try:
                k = statistics.mode(ks)
            except statistics.StatisticsError:
                k = random.choice(ks)
        else:
            # fully contained by coarse face
            if f in coarse.faces:
                t = f
            else:
                # edge face, is a vertex of parent grid, between three faces, exactly one of which
                # is also in the coarse grid
                t = [pf for pf in terrain.prev.vertices[f] if pf in coarse.faces][0]
            k = tiles[t].climate.koeppen
        if k[0] == u'E': return 0
        if not HistorySimulation.hasagriculture(f, population, agricultural): return 0.25
        if k in (u'BW', u'BS', u'Af'): return 0.15
        return 0.05

    @staticmethod
    def colornations(colors, cities, citytree, boundaries):
        while len(colors) < len(cities):
            colors.append(None)
        for c in set(boundaries.values()):
            # find the closest 6 cities
            ns = citytree.nearest(cities[c], 6)
            ncs = [colors[n] for n in ns if n in colors]
            if len(ncs) == len(ns):
                colors[c] = ncs[-1]
            else:
                colors[c] = random.choice(list(set(range(len(ns))) - set(ncs)))

    @staticmethod
    def nationalboundaries(colors, boundaries, terrain, elevation, rivers, adj, tiles, population, agricultural):
        start = time.time()
        cities = list({f for f in terrain.faces
                       if f in population and
                          random.random() < HistorySimulation.cityprob(f, terrain, tiles, population, agricultural)})
        # save state so the ultimate result isn't dependent on timing
        state = random.getstate()
        def tree():
            return PointTree(dict([[cities[i], i] for i in range(len(cities))]))
        citytree = tree()
        for f in terrain.faces:
            if f in population and sum([p.thousands for p in population[f]]) > 0:
                candidates = citytree.nearest(f, 6)
                paths, costs = [[f] for _ in candidates], [0 for _ in candidates]
                while True:
                    # find the cheapest path so far
                    i = min(range(len(paths)), key=lambda i: costs[i])
                    if costs[i] == float('inf'):
                        # found a new nation
                        cities.append(f)
                        citytree = tree()
                        boundaries[f] = len(cities)-1
                        break
                    city = cities[candidates[i]]
                    if paths[i][-1] == city:
                        boundaries[f] = candidates[i]
                        break
                    # advance it
                    step = min(adj[paths[i][-1]], key=lambda n: dist2(city, n))
                    paths[i].append(step)
                    if step not in elevation or elevation[step] <= 0:
                        # can't cross below sea level
                        costs[i] += float('inf')
                    elif step not in population or sum([p.thousands for p in population[step]]) <= 0:
                        # can't cross unpopulated terrain
                        costs[i] += float('inf')
                    elif (HistorySimulation.hasagriculture(f, population, agricultural) !=
                          HistorySimulation.hasagriculture(step, population, agricultural)):
                        # can't include both agricultural and exclusively pre-agricultural people
                        costs[i] += float('inf')
                    elif any([step in r for r in rivers]):
                        # difficult to span river
                        costs[i] += 10
                    else:
                        costs[i] += 1
            if time.time() - start > 5:
                HistorySimulation.colornations(colors, cities, citytree, boundaries)
                yield
                start = time.time()
        random.setstate(state)
        HistorySimulation.colornations(colors, cities, citytree, boundaries)

    @staticmethod
    def tilespecies(species, seasons):
        populations = {}
        for i in range(len(species)):
            for f in species[i].seasonalrange(len(seasons)):
                if f not in populations:
                    populations[f] = set()
                populations[f].add(i)
        return {f: sorted(ss) for (f, ss) in populations.items()}

    @staticmethod
    def facespecies(f, terrain, tilespecies):
        coarse = terrain.prev.prev
        population = set()
        if f in coarse.vertices:
            # face is a vertex of the coarse grid, get union of three
            for pf in coarse.vertices[f]:
                if pf not in tilespecies:
                    continue
                for si in tilespecies[pf]:
                    population.add(si)
        else:
            # fully contained by coarse face
            if f in coarse.faces:
                t = f
            else:
                # edge face, is a vertex of parent grid, between three faces, exactly one of which
                # is also in the coarse grid
                t = [pf for pf in terrain.prev.vertices[f] if pf in coarse.faces][0]
            if t in tilespecies:
                for si in tilespecies[t]:
                    population.add(si)
        return population

    def facespeciescount(self, f):
        return len(self.facespecies(f, self._terrain, self._tilespecies))

    @staticmethod
    def nationspecies(boundaries, terrain, tilespecies):
        coarse = terrain.prev.prev
        populations = []
        for f, i in boundaries.items():
            while i not in range(len(populations)):
                populations.append(set())
            populations[i] |= HistorySimulation.facespecies(f, terrain, tilespecies)
        return [sorted(ss) for ss in populations]

    def facenationspecies(self, f):
        if f in self.boundaries:
            return [self._species[s] for s in self._nationspecies[self.boundaries[f]]]
        return []

    def imports(self, n):
        resources = set()
        for partner in self.recursivetradepartners(n, self._tradepartners, {}):
            resources |= {('species', s) for s in self._nationspecies[partner] if s not in self._nationspecies[n]}
        return resources

    def exports(self, n):
        resources = set()
        for partner in self.lookuptradepartners(n, self._tradepartners):
            resources |= {('species', s) for s in self._nationspecies[n] if s not in self._nationspecies[partner]}
        return resources

    def resource(self, kind, index):
        if kind == 'species':
            return self._species[index]
        raise NotImplementedError("Don't know about {} resources".format(kind))

    @staticmethod
    def langfromspecies(nationspecies):
        for n in range(len(nationspecies)):
            ss = nationspecies[n]
            if len(ss) < minspecies:
                yield None
            else:
                vs, cs = phonemes()
                l = list(lexicon(vs, cs, round(random.gauss(-0.5, 1)), random.gauss(0.5, 0.1), random.gauss(0.5, 0.1), None, len(ss) + 1))
                random.shuffle(l)
                d = language.dictionary.Dictionary()
                for i in range(len(l)-1):
                    d.add(l[i], 'species', ss[i])
                d.add(l[-1], 'nation', n)
                yield d

    def language(self, n):
        return self._nationlangs[n]

    def facewordcount(self, f):
        if f in self.boundaries:
            n = self.boundaries[f]
            if n < len(self._nationlangs):
                return len(self._nationlangs[n].lexicon())
        return 0

    def loaddata(self, data, loadt):
        random.setstate(data['random'])
        loadt.start('initializing grid')
        self._initgrid(data['gridsize'])
        self.spin, self.cells, self.tilt = [data[k] for k in ['spin', 'cells', 'tilt']]
        self.tiles = data['tiles']
        self._tileloc = {t: f for f,t in self.tiles.items()}
        self.shapes = data['shapes']
        self.populated = data['population']
        self.agricultural = data['agricultural']
        self._glaciationt = data['glaciationtime']
        loadt.start('subdividing tiles')
        self._terrain = terrain(self.grid, self.tiles)
        self._terrainadj = Adjacency(self._terrain)
        self.terrainchanged = True
        loadt.start('determining elevation')
        self._elevation = {f: elevation(f, self._terrain, self.tiles) for f in self._terrain.faces}
        loadt.start('initializing indexes')
        self.initindexes()
        loadt.start('running rivers')
        self.rivers = riversmethod.run(self.tiles.values(), self._tileadj, self.minriverelev, self.minriverprecip)
        self.riverroutes = list(routerivers(
            self._terrain, self._terrainadj, {f: self.faceelevation(f) for f in self._terrain.faces},
            [[self._tileloc[t] for t in r] for r in self.rivers]))

        self._inited = data['historyinited']
        self._species = data['species']
        self._capacity = data['terraincap']
        self._population = data['terrainpop']
        self.nationcolors = data['nationcolors']
        self.boundaries = data['boundaries']
        self._tilespecies = data['tilespecies']
        self._nationspecies = data['nationspecies']
        self._nationlangs = data['nationlangs']
        self.phase = 'sim' if self._inited else 'uninit'

    def load(self, filename):
        loadt = self._timing.routine('loading state')
        loadt.start('reading file')
        self.loaddata(Data.load(filename), loadt)
        loadt.done()

    def savedata(self):
        return Data.savedata(random.getstate(), self._grid.size, 0, self.spin, self.cells, self.tilt, None, None, None, self.tiles, self.shapes, self._glaciationt, self.populated, self.agricultural, True, True, self._inited, self._species, self._capacity, self._population, self.nationcolors, self.boundaries, self._tilespecies, self._nationspecies, self._nationlangs)

    def save(self, filename):
        Data.save(filename, self.savedata())
