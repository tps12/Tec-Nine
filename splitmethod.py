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

def firstcorner(c, f):
    """Locate a corner of a square that would encompass a shape
    with the given center and furthest point."""
    cp = cross(c, f)
    ncp = norm(cp)
    d = atan2(ncp, dot(c, f))
    axis = cp/ncp
    f2 = rotate(c, cp/ncp, d * sqrt(2))
    return rotate(f2, c, pi/4)

def split(tiles):
    c = center(tiles)
    f = farthest(tiles, c.vector)

    # two random border angles separated by 120 degrees
    b1 = random() * 2*pi
    b2 = b1 + 2*pi/3
    bs = [b1, b2]

    # add any corners that fall in between (1 or 2)
    ths = [bs[0]] + [cn for cn in [i*pi/2 for i in range(1,5)] if bs[0] < cn < bs[1]] + [bs[1]]

    fc = firstcorner(c.vector, f.vector)

    # vectors for the corners of the split-off wedge
    vs = [rotate(fc, c.vector, th) for th in ths]

    # include center
    vs.append(c.vector)

    # velocity directions
    va = rotate(fc, c.vector, sum(bs)/2)
    va /= norm(va)
    vb = -va

    p = SphericalPolygon(vs)
    a, b = [], []
    for t in tiles:
        if p.contains(t.vector):
            a.append(t)
        else:
            b.append(t)

    if len(a) == 0 or len(b) == 0:
        return ((a+b, (0, 0, 0)),)

    return (a, va), (b, vb)
