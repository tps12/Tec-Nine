from cPickle import dump, load
from math import asin, acos, atan2, pi, exp, sqrt, sin, cos
import random

from numpy import *
from numpy.linalg import *

from sphericalpolygon import *

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
    
        # random location
        a = array([random.uniform(-1) for i in range(3)])
        p = a / norm(a)

        # best unit vector
        u = zeros(3)
        u[min(range(len(a)), key=lambda i: abs(p[i]))] = 1

        # random velocity vector
        v = cross(p, u)

        # random orienting point
        (o, ov) = apply_velocity(p, 0.05 * rotate(v / norm(v),
                                                  p,
                                                  random.uniform(0, 2*pi)))
        self.shape = [(.1,.23),(.12,.43),(.13,.52),(.25,.54),
                      (.3,.43),(.43,.48),(.53,.31),(.48,.14),
                      (.5,.1)]

        c = 0.25, 0.25

        coords = []
        for vertex in self.shape: 
            # find distance from centroid
            d = sqrt(sum([(vertex[i]-c[i])*(vertex[i]-c[i])
                          for i in range(2)]))
            d *= 10
            # find angle from local north
            th = atan2(vertex[0]-c[0],vertex[1]-c[1])

            # axis of rotation separating point from orientation point
            u = cross(p, o)
            u = u / norm(u)

            # rotate point around it by d
            rp = rotate(p, u, d)

            # and then around point by -theta
            rp = rotate(rp, p, -th)

            lat = atan2(rp[2], sqrt(rp[0]*rp[0] + rp[1]*rp[1])) * 180/pi
            lon = atan2(rp[1], rp[0]) * 180/pi
            coords.append((lat,lon))

        shape = SphericalPolygon(coords)
        for y in range(len(self.tiles)):
            if shape.latrange.min <= self.tiles[y][0][0] <= shape.latrange.max:
                for x in range(len(self.tiles[y])):
                    if shape.lonrange.min <= self.tiles[y][x][1] <= shape.lonrange.max:
                        if shape.contains(self.tiles[y][x][0:2]):
                            self.tiles[y][x] = (self.tiles[y][x][0],
                                                self.tiles[y][x][1],
                                                1)

    def update(self):
        pass
