from cPickle import dump, load
from itertools import combinations
from math import asin, acos, atan2, pi, exp, sqrt, sin, cos
from multiprocessing import cpu_count, Pool
import random

from numpy import *
from numpy.linalg import *

from latrange import *
from sphericalpolygon import *

from adjacency import *
from shape import *
from tile import *

def bearing(c1, c2):
    lat1, lon1 = [c * pi/180 for c in c1]
    lat2, lon2 = [c * pi/180 for c in c2]

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    theta = atan2(sin(dlon) * cos(lat2),
                  cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon))
    return (theta * 180/pi) % 360   

def rotate(p, axis, theta):
    # http://inside.mines.edu/~gmurray/ArbitraryAxisRotation/ArbitraryAxisRotation.html
    L2 = sum([i*i for i in axis])
    return array([(axis[0]*sum(p * axis) +
                   (p[0]*(axis[1]*axis[1]+axis[2]*axis[2]) +
                    axis[0]*(-axis[1]*p[1]-axis[2]*p[2])) * cos(theta) +
                   sqrt(L2)*(-axis[2]*p[1]+axis[1]*p[2]) * sin(theta))/L2,
                  (axis[1]*sum(p * axis) +
                   (p[1]*(axis[0]*axis[0]+axis[2]*axis[2]) +
                    axis[1]*(-axis[0]*p[0]-axis[2]*p[2])) * cos(theta) +
                   sqrt(L2)*(axis[2]*p[0]-axis[0]*p[2]) * sin(theta))/L2,
                  (axis[2]*sum(p * axis) +
                   (p[2]*(axis[0]*axis[0]+axis[1]*axis[1]) +
                    axis[2]*(-axis[0]*p[0]-axis[1]*p[1])) * cos(theta) +
                   sqrt(L2)*(-axis[1]*p[0]+axis[0]*p[1]) * sin(theta))/L2])
                   
def apply_velocity(p, v):
    d = norm(v)

    if d:
        axis = cross(p, v)
        axis = axis / norm(axis)

        return tuple([rotate(i, axis, d) for i in (p,v)])
    else:
        return p, v

def _iteratelat(latdata):
    """Set tile values for the given latitude array."""
    lat, shapes = latdata
    inlatrange = [i for i in range(len(shapes))
                  if shapes[i].latrange.contains(lat[0].lat)]
    for x in range(len(lat)):
        lat[x].overlapping = []
        for i in [i for i in inlatrange
                  if shapes[i].lonrange.contains(lat[x].lon)]:
            if shapes[i].contains(lat[x].vector):
                lat[x].overlapping.append(i)
    return lat

class PlanetSimulation(object):
    
    def __init__(self, r, dt):
        """Create a simulation for a planet of radius r km and timesteps of dt
        million years.
        """
        # max speed is 100km per million years
        self._dp = 100.0/r * dt

        self._erode = dt

        degrees = 2

        self.tiles = []
        for lat in range(-89, 91, degrees):
            r = cos(lat * pi/180)
            row = []
            d = 2 / r
            lon = d/2
            while lon <= 180:
                flat = float(lat)
                row = ([Tile(flat, -lon)] +
                       row +
                       [Tile(flat, lon)])
                lon += d
            self.tiles.append(row)

        self.adj = Adjacency(self.tiles)
                
        xmax = max([len(self.tiles[i]) for i in range(len(self.tiles))])

        dimensions = xmax, len(self.tiles)
   
        # initial location
        p = (0, 1, 0)

        # 0 velocity vector
        v = (0, 0, 0)

        # orienting point
        o = (1, 0, 0)

        r = 1.145
        shape = [(r*random.uniform(0.9,1.1)*cos(th),
                  r*random.uniform(0.9,1.1)*sin(th))
                 for th in [i*pi/8 for i in range(16)]]

        self._shapes = [Shape(shape, p, o, v)]

        self._pool = Pool(processes=cpu_count())

    def update(self):
        """Update the simulation by one timestep.

        This consists of:
        1. applying velocities to each continent shape,
        2. projecting each shape's 2D boundary onto the sphere, and
        3. updating the tiles with the shapes that contain them.
        """
        for s in self._shapes:
            s.apply_velocity(self._dp)

        shapes = [s.projection() for s in self._shapes]

        self.tiles = self._pool.map(_iteratelat, [(lat, shapes) for lat in self.tiles])

        collisions = {}
        for lat in self.tiles:
            for tile in lat:
                previous = tile.value
                tile.value = 0
                for i in tile.overlapping:
                    tile.value += self._shapes[i].historicalvalue(tile.vector)
                if tile.value == 0:
                    tile.value = len(tile.overlapping)
                for pair in combinations(tile.overlapping, 2):
                    if pair not in collisions:
                        collisions[pair] = 1
                    else:
                        collisions[pair] += 1
                if tile.value > 0 and previous == 0:
                    tile.value += 1
                if tile.value > 10:
                    tile.value = 10

        # erode to lower adjacent tiles
        for e in range(self._erode):
            dv = [[0 for j in range(len(self.tiles[i]))] for i in range(len(self.tiles))]
            for i in range(len(self.tiles)):
                for j in range(len(self.tiles[i])):
                    tile = self.tiles[i][j]
                    if tile.value > 0:
                        adj = self.adj[(j,i)]
                        for (j2,i2) in adj:
                            d = tile.value - self.tiles[i2][j2].value
                            if d > 0:
                                d /= (5 * len(adj))
                                dv[i][j] -= d
                                dv[i2][j2] += d

            for i in range(len(self.tiles)):
                for j in range(len(self.tiles[i])):
                    self.tiles[i][j].value += dv[i][j]

        for shape in self._shapes:
            shape.resethistory()

        for lat in self.tiles:
            for tile in lat:
                if tile.value > 0:
                    for i in tile.overlapping:
                        self._shapes[i].recordvalue(tile.vector, tile.value)

        # merge shapes that overlap a lot
        for (pair, count) in collisions.items():
            if count > min([self._shapes[i].area for i in pair])/10:
                self._shapes[pair[0]].merge(self._shapes.pop(pair[1]))
                break

        # occaisionally split big shapes
        for i in range(len(self._shapes)):
            if random.uniform(0,1) > 1/self._shapes[i].area:
                self._shapes[i:i+1] = self._shapes[i].split()

        self.dirty = True
