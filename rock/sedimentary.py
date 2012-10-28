def deposit(materials, life, sea, climate):
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

    rock = { 'type': 'S', 'name': None }
    thickness = sum([c['thickness'] for c in contributions])
    for k in depositkeys:
        if k not in rock:
            # weight attributes by thickness
            rock[k] = sum([float(c['thickness']) * c['rock'][k]
                           if k in c['rock'] else 0
                           for c in contributions])/thickness

    rock['clasticity'] = rock['clasticity'] * 2 if 'clasticity' in rock else 1

    if life:
        if sea:
            rock['calcity'] = max(0, min(1, float(climate.temperature - 18)/25))
            if rock['calcity'] > 0.99:
                rock['name'] = 'chalk'
            elif rock['calcity'] > 0.75:
                rock['name'] = 'limestone'
        elif climate.koeppen[0] == u'C' and climate.temperature < 18:
            rock['bogginess'] = max(0, (climate.precipitation - 0.75) * 4)

    if rock['name'] is None:
        grain = 1e-3/float(rock['clasticity'])
        if grain < 4e-6:
            name = 'claystone'
        elif grain < 60e-6:
            name = 'siltstone'
        elif grain < 2e-3:
            name = 'sandstone'
        else:
            name = 'conglomerate'
        rock['name'] = name

    return { 'rock': rock, 'thickness': thickness }
