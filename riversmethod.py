import random

import disjoint
import passability
import race

def follow(tile, adj, seen=None):
  seen = set() if seen is None else seen
  if tile.elevation <= 0:
    return [tile]
  for n in sorted(adj[tile], key=lambda t: t.elevation):
    if n in seen:
      continue
    sink = follow(n, adj, seen | {tile})
    if sink:
      return [tile] + sink

def get(tiles, adj, hmin, pmin):
  for t in tiles:
    if t.elevation > 0 and all([t.elevation >= n.elevation for n in adj[t]]):
      if t.elevation >= hmin:
        ts = follow(t, adj)
        if ts:
          p = 0
          for i in range(len(ts)):
            p += ts[i].climate.precipitation if ts[i].climate else 0
            if ts[i].climate and ts[i].climate.koeppen[0] != u'E' and p >= pmin:
              yield {t for t in ts[i:]}
              break

def run(tiles, adj, hmin, pmin):
  return list(get(tiles, adj, hmin, pmin))
