def deposit(materials):
    contributions = []
    depositkeys = set()
    for m in materials:
        t = 0
        i = len(m.substance[1]) - 1
        sources = []
        keys = set()
        while t < m.total:
            dt = m.total - t
            layer = m.substance[1][i]
            if layer['thickness'] >= dt:
                sources.append({ 'rock': layer['rock'], 'thickness': dt })
            else:
                sources.append(layer)
            keys = keys.union(sources[-1]['rock'].keys())
            t += sources[-1]['thickness']
            i -= 1

        rock = { 'type': 'S', 'name': 'S' }
        for k in keys:
            if k not in rock:
                # weight attributes by thickness
                rock[k] = sum([float(s['thickness']) * s['rock'][k]
                               if k in s['rock'] else 0
                               for s in sources])/m.total
        depositkeys = depositkeys.union(rock.keys())
        contributions.append({ 'rock': rock, 'thickness': m.amount })

    rock = { 'type': 'S', 'name': 'S' }
    thickness = sum([c['thickness'] for c in contributions])
    for k in depositkeys:
        if k not in rock:
            # weight attributes by thickness
            rock[k] = sum([float(c['thickness']) * c['rock'][k]
                           if k in c['rock'] else 0
                           for c in contributions])/thickness

    return { 'rock': rock, 'thickness': thickness }
