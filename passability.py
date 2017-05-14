def passable(t):
    return t.elevation > 0 and t.climate and t.climate.koeppen != u'BW' and t.climate.koeppen[0] != u'E'  # Not desert or polar

def hoppable(t):
    return t.elevation <= 0 or passable(t)

def expand(ts, adj, condition=hoppable):
    nextadjs = set()
    for n in ts:
        if condition(n):
            nextadjs |= set([a for a in adj[n] if condition(a)])
    return nextadjs

def within(t, adj, d, condition=hoppable):
    adjs = {t}
    for _ in range(d):
        adjs = expand(adjs, adj, condition)
    return adjs
