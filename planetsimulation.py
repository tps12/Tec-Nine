from cPickle import dump, load
from math import asin, acos, atan2, pi, exp, sqrt, sin, cos
from multiprocessing import cpu_count, Pool
import random

from numpy import *
from numpy.linalg import *

from latrange import *
from sphericalpolygon import *

from shape import *

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
    lat, shapes = latdata
    inlatrange = [s for s in shapes
                  if s.latrange.contains(lat[0][0])]
    if inlatrange:
        cos_lat = cos(lat[0][0] * pi/180)
        z = sin(lat[0][0] * pi/180)
    for x in range(len(lat)):
        value = 0
        for s in [s for s in inlatrange
                  if s.lonrange.contains(lat[x][1])]:
            v = (cos_lat * cos(lat[x][1] * pi/180),
                 cos_lat * sin(lat[x][1] * pi/180),
                 z)
            if s.contains(v):
                value += 1
        lat[x] = (lat[x][0], lat[x][1], value)
    return lat

class PlanetSimulation(object):
    
    def __init__(self):
        degrees = 2

        self.tiles = []
        for lat in range(-89, 91, degrees):
            r = cos(lat * pi/180)
            row = []
            d = 2 / r
            lon = d/2
            while lon <= 180:
                flat = float(lat)
                row = ([(flat, -lon, 0)] +
                       row +
                       [(flat, lon, 0)])
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
        shape = [(r*cos(th), r*sin(th))
                 for th in [i*pi/8 for i in range(16)]]

        c = 0, 0

        scale = 1

        coords = []
        for vertex in shape: 
            # find distance from centroid
            d = sqrt(sum([(vertex[i]-c[i])*(vertex[i]-c[i])
                          for i in range(2)])) * scale

            # find angle from local north
            th = atan2(vertex[0]-c[0],vertex[1]-c[1])
            
            coords.append((d, th))

        self._shapes = [Shape(coords, p, o, v)]

        self._pool = Pool(processes=cpu_count())

    def update(self):
        for s in self._shapes:
            s.apply_velocity(0.01)

        shapes = [s.projection() for s in self._shapes]

        self.tiles = self._pool.map(_iteratelat, [(lat, shapes) for lat in self.tiles])
        self.dirty = True
