def zeolite(layer):
    rock = layer['rock'].copy()
    if 'clasticity' in rock:
        rock['type'] = 'M'
        grain = 1e-3/float(rock['clasticity'])
        if grain < 60e-6:
            name = 'pelite'
        elif grain < 2e-3:
            name = 'psammite'
        else:
            name = 'psephite'
        del rock['clasticity']
        rock['name'] = name
    return { 'rock': rock, 'thickness': layer['thickness'] }

def blueschist(layer):
    rock = layer['rock'].copy()
    rock['type'] = 'M'
    rock['name'] = 'blueschist'
    return { 'rock': rock, 'thickness': layer['thickness'] }

def greenschist(layer):
    rock = layer['rock'].copy()
    rock['type'] = 'M'
    rock['name'] = 'greenschist'
    return { 'rock': rock, 'thickness': layer['thickness'] }

def amphibolite(layer):
    rock = layer['rock'].copy()
    rock['type'] = 'M'
    rock['name'] = 'amphibolite'
    return { 'rock': rock, 'thickness': layer['thickness'] }

def eclogite(layer):
    rock = layer['rock'].copy()
    rock['type'] = 'M'
    rock['name'] = 'eclogite'
    return { 'rock': rock, 'thickness': layer['thickness'] }

lowgrade = [
    (5, lambda l: l),
    (15, zeolite),
    (30, greenschist),
    (70, amphibolite),
    (float('inf'), eclogite)
]

normal = [
    (10, lambda l: l),
    (20, zeolite),
    (60, blueschist),
    (float('inf'), eclogite)
]

def transform(layers, subduction):
    facies = lowgrade if subduction else normal
    f = 0
    newlayers = []
    # accumulate depth from top down
    t = 0
    layers = list(layers)
    while len(layers) > 0:
        l = layers.pop()

        dt = t + l['thickness'] - facies[f][0]
        if dt > 0:
            # split along the boundary
            layers.append({ 'rock': l['rock'], 'thickness': dt })
            l['thickness'] -= dt

        newlayers.append(facies[f][1](l))
        t += l['thickness']
        if dt > 0:
            f += 1

    return list(reversed(newlayers))
