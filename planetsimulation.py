from cPickle import dump, load
from math import asin, acos, atan2, pi, exp, sqrt, sin, cos
from multiprocessing import cpu_count, Pool
import random

from numpy import *
from numpy.linalg import *

from latrange import *
from sphericalpolygon import *

from shape import *
from tile import *

def distance(c1, c2):
    lat1, lon1 = [c * pi/180 for c in c1]
    lat2, lon2 = [c * pi/180 for c in c2]

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * atan2(sqrt(a), sqrt(1-a))

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
        
        xmax = max([len(self.tiles[i]) for i in range(len(self.tiles))])

        dimensions = xmax, len(self.tiles)
   
        # initial location
        p = (0, 1, 0)

        # unit vector
        u = (0, 0, 1)

        # 0 velocity vector
        v = (0, 0, 0)

        # orienting point
        o = (1, 0, 0)

        r = 1.145
        shape = [(r*random.uniform(0.9,1.1)*cos(th),
                  r*random.uniform(0.9,1.1)*sin(th))
                 for th in [random.uniform(0.9,1.1)*i*pi/8 for i in range(16)]]

        self._shapes = Shape(shape, p, o, v).split()

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
        for lat in self.tiles:
            for tile in lat:
                previous = tile.value
                tile.value = 0
                for i in tile.overlapping:
                    tile.value += self._shapes[i].historicalvalue(tile.vector)
                if tile.value == 0:
                    tile.value = len(tile.overlapping)
                if tile.value > 0 and previous == 0:
                    tile.value += 1
                if tile.value > 10:
                    tile.value = 10
                if tile.value > 0:
                    for i in tile.overlapping:
                        self._shapes[i].recordvalue(tile.vector, tile.value)
        self.dirty = True
