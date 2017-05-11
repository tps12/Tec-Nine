import random

def sea(tiles):
  return [t for t in tiles.itervalues() if t.elevation <= 0]

# TODO: optimize (currently O(n^2), could be O(nlogn)?)
def mainocean(seatiles, adj):
  bodies = []
  for t in seatiles:
    for n in adj[t]:
      if n in seatiles:
        equiv = set()
        for i in range(len(bodies)):
          if n in bodies[i]:
            bodies[i].add(t)
            equiv.add(i)
          if t in bodies[i]:
            bodies[i].add(n)
            equiv.add(i)
        if not equiv:
          bodies.append({t,n})
        else:
          bodies = (
              [reduce(lambda a,b: a|b, [bodies[i] for i in equiv], set())] +
              [bodies[i] for i in range(len(bodies)) if i not in equiv])
  return sorted(bodies, key=len)[-1]

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
