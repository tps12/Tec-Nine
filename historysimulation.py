import math
import random
import statistics
import time

from dist2 import dist2
from grid import Grid
from hexadjacency import Adjacency
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

class HistorySimulation(object):
    coastprox = PrehistorySimulation.coastprox
    minriverelev = PrehistorySimulation.minriverelev
    minriverprecip = PrehistorySimulation.minriverprecip

    _timing = Timing()

    def __init__(self, gridsize):
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

        self._capacity = self.capacity(self.grid, self.tiles, self._terrain, self._tileadj, [])
        self._population = self.population(self.grid, self.tiles, self._terrain, self.populated, self.agricultural)

        self.nations = []
        self.boundaries = {}

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

    def update(self):
        stept = self._timing.routine('simulation step')

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
                self.boundaries[f] = random.choice(list(nations))

        stept.start('removing empty populations')
        for ps in self._population.values():
            for i in [i for i in reversed(range(len(ps))) if not ps[i].thousands]:
                del ps[i]

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
    def settlespecies(tiles, adj, timing):
        fauna, plants, trees = [], [], []
        lifeformsmethod.settle(fauna, plants, trees, tiles, adj, timing)
        return fauna + plants + trees

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
    def nationalboundaries(terrain, elevation, rivers, adj, tiles, population, agricultural, loadt):
        loadt.start('creating national boundaries')
        cities = list({f for f in terrain.faces
                       if f in population and
                          random.random() < HistorySimulation.cityprob(f, terrain, tiles, population, agricultural)})
        def tree():
            return PointTree(dict([[cities[i], i] for i in range(len(cities))]))
        citytree = tree()
        boundaries = {}
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
        return [None for _ in range(len(cities))], boundaries

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
        loadt.start('subdividing tiles')
        self._terrain = terrain(self.grid, self.tiles)
        self._terrainadj = Adjacency(self._terrain)
        self.terrainchanged = True
        loadt.start('determining elevation')
        self._elevation = {f: elevation(f, self._terrain, self.tiles) for f in self._terrain.faces}
        loadt.start('initializing indexes')
        self.initindexes()
        self._species = self.settlespecies(self.tiles, self.adj, loadt)
        loadt.start('running rivers')
        self.rivers = riversmethod.run(self.tiles.values(), self._tileadj, self.minriverelev, self.minriverprecip)
        self.riverroutes = list(routerivers(
            self._terrain, self._terrainadj, {f: self.faceelevation(f) for f in self._terrain.faces},
            [[self._tileloc[t] for t in r] for r in self.rivers]))
        loadt.start('determining carrying capacities')
        self._capacity = self.capacity(self.grid, self.tiles, self._terrain, self._tileadj, self.rivers)
        loadt.start('determining population')
        self._population = self.population(self.grid, self.tiles, self._terrain, self.populated, self.agricultural)
        self.nations, self.boundaries = self.nationalboundaries(
            self._terrain, self._elevation, self.riverroutes, self._terrainadj, self.tiles, self._population, self.agricultural, loadt)
        self._glaciationt = data['glaciationtime']

    def load(self, filename):
        loadt = self._timing.routine('loading state')
        loadt.start('reading file')
        self.loaddata(Data.load(filename), loadt)
        loadt.done()

    def savedata(self):
        return Data.savedata(random.getstate(), self._grid.size, 0, self.spin, self.cells, self.tilt, None, None, None, self.tiles, self.shapes, self._glaciationt, self.populated, self.agricultural, True, True)

    def save(self, filename):
        Data.save(filename, self.savedata())
