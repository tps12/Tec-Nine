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
    rock['name'] = 'schist'
    return { 'rock': rock, 'thickness': layer['thickness'] }

facies = [
    (10, lambda l: l),
    (20, zeolite),
    (float('inf'), blueschist)
]

def transform(layers):
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
