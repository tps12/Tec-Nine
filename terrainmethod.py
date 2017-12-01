from noise import snoise3

from dist2 import dist2
from grid import Grid

def terrain(grid, tiles):
    # first level, populate every land tile
    terrain = Grid(grid)
    for v, t in tiles.items():
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

# greedily find next path toward edge goal terrain tiles, going through lowest elevation adjacent tile at each step
def findpath(source, edge, pool, seen, adj, elevation):
    seen.add(source)
    if source in edge:
        return [source]
    for n in sorted(adj[source], key=lambda n: elevation[n] if n in elevation else 0):
        if n in pool and n not in seen:
            steps = findpath(n, edge, pool, seen, adj, elevation)
            if steps is not None:
                return [source] + steps
    return None

def routerivers(terrain, adj, elevation, rivers):
    children = {}
    def insertorappend(k, v):
        if k in children:
            children[k].append(v)
        else:
            children[k] = [v]
    coarse = terrain.prev.prev
    for f in terrain.faces:
        if f in coarse.vertices:
            # face is a vertex of the coarse grid, child of three coarse faces
            for pf in coarse.vertices[f]:
                insertorappend(pf, f)
        else:
            if f in coarse.faces:
                # fully contained by coarse face
                insertorappend(f, f)
            else:
                # edge face, is a vertex of parent grid, between three faces, exactly one of which
                # is also in the coarse grid
                pf = [pf for pf in terrain.prev.vertices[f] if pf in coarse.faces][0]
                insertorappend(pf, f)

    for r in rivers:
        route = [r[0]]
        for i in range(len(r)):
            pool = children[r[i]]
            if i < len(r)-1:
                # goal is any of the three faces bordering the next coarse face
                edge = sorted(pool, key=lambda f: dist2(f, r[i+1]))[:3]
            else:
                # goal is any face bordering sea: as heuristic, lowest elevation
                edge = sorted(pool, key=lambda f: elevation[f] if f in elevation else 0)[:1]
            route += findpath(route[-1], edge, pool, set(), adj, elevation)
        yield route
