def passable(t):
    return t.elevation <= 0 or (t.climate and t.climate.koeppen != u'BW' and t.climate.koeppen[0] != u'E')  # Not desert or polar

def expand(ts, adj):
    nextadjs = set()
    for n in ts:
        if passable(n):
            nextadjs |= set([a for a in adj[n] if passable(a)])
    return nextadjs

def within(t, adj, d):
    adjs = {t}
    for _ in range(d):
        adjs = expand(adjs, adj)
    return adjs
