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

def expandfrontier(frontier, seatiles, adj, populated):
    newfrontier = set()
    for t in frontier:
        for n in adj[t]:
            if (n not in seatiles and any([nn in seatiles for nn in adj[n]]) and  # On coast
                n not in frontier and n not in populated and  # Not visited yet
                (n.climate.koeppen == u'Aw' or n.climate.koeppen[0] in u'CD')):  # Savannah or temperate/cold
                newfrontier.add(n)
    return (populated | frontier), newfrontier
