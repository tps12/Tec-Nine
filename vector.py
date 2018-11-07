import math

def centroid(points, weights=None):
    weights = weights if weights is not None else [1 for _ in points]
    assert len(points) == len(weights)
    assert len(points) > 0
    assert all([len(p) == len(points[0]) for p in points])
    totals, total_weight = [0 for _ in points[0]], 0
    for i in range(len(points)):
        for j in range(len(totals)):
            totals[j] += points[i][j] * weights[i]
        total_weight += weights[i]
    assert total_weight > 0
    return [total/total_weight for total in totals]

def diff(a, b):
    assert len(a) == len(b)
    return [a[i] - b[i] for i in range(len(a))]

def add(a, b):
    assert len(a) == len(b)
    return [a[i] + b[i] for i in range(len(a))]

def length(v):
    return math.sqrt(sum([m**2 for m in v]))

def scalemax(v, l):
    vlen = length(v)
    if vlen > l:
        return [l*m/vlen for m in v]
    return v
