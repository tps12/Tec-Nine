import random

import disjoint

def sea(tiles):
  return [t for t in tiles.itervalues() if t.elevation <= 0]

def mainocean(seatiles, adj):
  seas = {t: disjoint.set() for t in seatiles}
  for t in seatiles:
    for n in adj[t]:
      if n in seatiles:
        disjoint.union(seas[t], seas[n])
  bodies = {}
  for t in seatiles:
    s = seas[t].root()
    if s not in bodies:
      bodies[s] = set()
    bodies[s].add(t)
  return sorted(bodies.values(), key=len)[-1]

def eden(tiles, seatiles, adj):
    o = mainocean(seatiles, adj)
    candidates = [t for t in tiles.itervalues()
                  if t.climate and t.climate.koeppen == u'Aw' and
                  any([n in o for n in adj[t]])]
    return {random.choice(candidates)} if candidates else set()

def passable(t):
    return t.elevation <= 0 or (t.climate and t.climate.koeppen != u'BW' and t.climate.koeppen[0] != u'E')  # Not desert or polar

def expandpassable(ts, adj):
    nextadjs = set()
    for n in ts:
        if passable(n):
            nextadjs |= set([a for a in adj[n] if passable(a)])
    return nextadjs

def within(t, adj, d):
    adjs = {t}
    for _ in range(d):
        adjs = expandpassable(adjs, adj)
    return adjs

def nearcoast(t, adj, d):
    return t.elevation > 0 and any([n.elevation <= 0 for n in within(t, adj, d)])

def habitable(t):
    return t.elevation > 0 and (t.climate.koeppen == u'Aw' or t.climate.koeppen[0] in u'CD')  # Savannah or temperate/cold

def expandfrontier(frontier, seatiles, adj, populated, travelrange, coastalproximity):
    newfrontier = set()
    for t in frontier:
        distance = 0
        adjs = adj[t]
        while distance < travelrange:
            added = False
            for n in adjs:
                if (nearcoast(n, adj, coastalproximity) and
                    n not in frontier and n not in populated and  # Not visited yet
                    habitable(n)):
                    newfrontier.add(n)
                    added = True
            if added: break
            adjs = sorted(list(expandpassable(adjs, adj)))
            distance += 1
    return (populated | frontier), newfrontier
