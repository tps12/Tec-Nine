from noise import snoise3

from grid import Grid

def terrain(grid, tiles):
    # first level, populate every land tile
    terrain = Grid(grid)
    for v, t in tiles.iteritems():
        if t.elevation > 0:
            terrain.populate(v)
    # then subdivide that
    for _ in range(1):
        terrain = Grid(terrain)
        for v in list(terrain.prev.faces.keys()):
            terrain.populate(v)
    return terrain

def components(f, grid, tiles):
    if f in tiles:
        # face has a tile, just return it
        return [[tiles[f]]]
    if f in grid.vertices:
        # average adjacent faces
        return [sum([components(vf, grid, tiles)
                     for vf in grid.vertices[f]], [])]
    # otherwise check in parent
    return [components(f, grid.prev, tiles)]

def interpolate(f, ts):
    if not hasattr(ts, '__iter__'):
        return float(f(ts))
    vs = [interpolate(f, t) for t in ts]
    return sum(vs)/len(vs)

def elevation(f, ter, tiles):
    ts = components(f, ter, tiles)
    return interpolate(lambda t: t.elevation, ts) + interpolate(lambda t: t.mountainosity, ts) * snoise3(f[0], f[1], f[2], 7, 0.85)
