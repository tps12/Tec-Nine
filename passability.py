def passable(t, agricultural):
    # Pre-agricultural people can't pass through desert or any polar climate; agricultural only blocked by ice cap
    impassable_climates = {u'EF'} if agricultural else {u'BW', u'ET', u'EF'}
    return t.elevation > 0 and t.climate and t.climate.koeppen not in impassable_climates

def hoppable(t, agricultural):
    return t.elevation <= 0 or passable(t, agricultural)

def expand(ts, adj, agricultural, condition=hoppable):
    nextadjs = set()
    for n in ts:
        if condition(n, agricultural):
            nextadjs |= set([a for a in adj[n] if condition(a, agricultural)])
    return nextadjs

def within(t, adj, d, agricultural, condition=hoppable):
    adjs = {t}
    for _ in range(d):
        adjs = expand(adjs, adj, agricultural, condition)
    return adjs
