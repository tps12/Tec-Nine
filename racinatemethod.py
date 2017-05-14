import disjoint
import passability

def racinate(tiles, adj, populated, travelrange):
  pops = {t: disjoint.set() for t in populated}
  for t in populated:
    for n in passability.within(t, adj, travelrange):
      if n in populated:
        disjoint.union(pops[t], pops[n])
  races = {}
  for t in populated:
    r = pops[t].root()
    if r not in races:
      races[r] = set()
    races[r].add(t)
  return sorted(races.values(), key=len)
