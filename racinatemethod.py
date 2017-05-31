import disjoint
import passability
import race

def racinate(tiles, adj, populated, agricultural, travelrange):
  pops = {t: disjoint.set() for t in populated}
  for t, r in populated.iteritems():
    for n in passability.within(t, adj, travelrange, r in agricultural, passability.passable):
      if n in populated:
        disjoint.union(pops[t], pops[n])
  races = {}
  for t in populated:
    r = pops[t].root()
    if r not in races:
      races[r] = set()
    races[r].add(t)
  # if any geographically isolated race has >1 heritages, combine them into a new one
  for ts in races.itervalues():
    hs = {populated[t] for t in ts}
    if len(hs) > 1:
      h = race.Heritage(hs)
      if any([r in agricultural for r in hs]):
        agricultural.add(h)
      for t in ts:
        populated[t] = h
  # if any heritage appears in >1 geographically isolated race, branch it into new ones
  heritageraces = {}
  for r, ts in races.iteritems():
    for h in {populated[t] for t in ts}:
      if h not in heritageraces:
        heritageraces[h] = {r}
      else:
        heritageraces[h].add(r)
  for h, rs in heritageraces.iteritems():
    if len(rs) > 1:
      for r in rs:
        nh = race.Heritage({h})
        if h in agricultural:
          agricultural.add(nh)
        for t in races[r]:
          populated[t] = nh
