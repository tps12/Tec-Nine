from math import pi, sqrt, atan2, sin, cos
from random import random

from numpy import array, cross, dot
from numpy.linalg import norm

from sphericalpolygon import SphericalPolygon

def rotate(p, axis, theta):
    """Rotate a vector about an axis by a specified amount."""
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

def average(vs):
    """Average a list of vectors."""
    a = [0, 0, 0]
    for v in vs:
        for i in range(len(a)):
            a[i] += v[i]
    return [float(c)/len(vs) for c in a]

def center(tiles):
    """Get the tile closest to the average location of the given tiles."""
    a = average([t.vector for t in tiles])
    return closest(tiles, a)

def mostest(tiles, p, fn):
    """Return the most whatevery tile relative to a point,
    given a comparison function that evaluates whateveriness.
    """
    m, md2 = None, None
    for tile in tiles:
        d2 = sum([(tile.vector[i]-p[i])**2 for i in range(len(p))])
        if md2 is None or fn(d2, md2):
            m = tile
            md2 = d2
    return m

def closest(tiles, p):
    """Get the closest tile to a point."""
    return mostest(tiles, p, lambda d2, md2: d2 < md2)

def farthest(tiles, p):
    """Get the farthest tile from a point."""
    return mostest(tiles, p, lambda d2, md2: d2 > md2)

def move(tiles, group, v, index, indexedtiles):
    for t in tiles:
        t.value = 0

    for t in group:
        t.value = 2

    vs = [t.vector for t in group]
    a = average(vs)
    a /= norm(a)

    axis = cross(a, v)
    axis /= norm(axis)

    speed = norm(v)

    for i in range(len(vs)):
        loc = list(rotate(vs[i], axis, speed))
        k = 0
        while True:
            t = indexedtiles[list(index.nearest(loc, k+1))[k]]
            if t.value != 1:
                t.value = 1
                break
            k += 1

    vp = rotate(v, axis, speed)
    for i in range(len(v)):
        v[i] = vp[i]
