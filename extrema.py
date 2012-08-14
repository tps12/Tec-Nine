def findextrema(items, compare):
    if len(items) == 0: raise ValueError('Must have at least one item in list')
    if len(items) == 1: return [0]
    extrema = []
    candidates = []
    for i in range(-1, len(items)):
        # if this one's better than the last
        if compare(items[i], items[i-1]):
            # it's a candidate for an extreme
            candidates = [i]
        # if the last wasn't better than this
        elif not compare(items[i-1], items[i]) and len(candidates) > 0:
            # they're equally good
            candidates.append(i)
        # any candidates we had were winners
        else:
            extrema += [c % len(items) for c in candidates]
            candidates = []
    return sorted(list(set(extrema)))
