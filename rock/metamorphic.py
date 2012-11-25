from math import isinf, sqrt

IDENTITY = object()

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
        rock['toughness'] = max(0.25, rock['toughness'])
    return { 'rock': rock, 'thickness': layer['thickness'] }

def blueschist(layer):
    rock = layer['rock'].copy()
    rock['type'] = 'M'
    rock['name'] = 'blueschist'
    rock['toughness'] = max(0.75, rock['toughness'])
    return { 'rock': rock, 'thickness': layer['thickness'] }

def greenschist(layer):
    rock = layer['rock'].copy()
    rock['type'] = 'M'
    rock['name'] = 'greenschist'
    rock['toughness'] = max(0.75, rock['toughness'])
    return { 'rock': rock, 'thickness': layer['thickness'] }

def amphibolite(layer):
    rock = layer['rock'].copy()
    rock['type'] = 'M'
    rock['name'] = 'amphibolite'
    rock['toughness'] = max(0.8, rock['toughness'])
    return { 'rock': rock, 'thickness': layer['thickness'] }

def eclogite(layer):
    rock = layer['rock'].copy()
    rock['type'] = 'M'
    rock['name'] = 'eclogite'
    rock['toughness'] = max(0.85, rock['toughness'])
    return { 'rock': rock, 'thickness': layer['thickness'] }

def hornfels(layer):
    rock = layer['rock'].copy()
    rock['type'] = 'M'
    rock['name'] = 'hornfels'
    rock['toughness'] = 1
    return { 'rock': rock, 'thickness': layer['thickness'] }

def granulite(layer):
    rock = layer['rock'].copy()
    rock['type'] = 'M'
    rock['name'] = 'granulite'
    rock['toughness'] = 1
    return { 'rock': rock, 'thickness': layer['thickness'] }

def marblize(rock):
    if 'calcity' in rock and rock['calcity'] > 0.75:
        rock['name'] = 'marble'
    return rock

def transform(layers, facies):
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

        if facies[f][1] is not IDENTITY:
            l = facies[f][1](l)
            l['rock'] = marblize(l['rock'])

        newlayers.append(l)
        t += l['thickness']
        if dt > 0:
            f += 1

    return list(reversed(newlayers))

# max depth/facies function pairs
normal = [
    (5, IDENTITY),
    (15, zeolite),
    (30, greenschist),
    (70, amphibolite),
    (float('inf'), eclogite)
]

lowtemp = [
    (10, IDENTITY),
    (20, zeolite),
    (60, blueschist),
    (float('inf'), eclogite)
]

def regional(layers, subduction):
    return transform(layers, lowtemp if subduction else normal)

# max temperature/facies function pairs
hightemp = [
    (250, IDENTITY),
    (800, hornfels),
    (float('inf'), granulite)
]

def intrusiontemperature(depth):
    # temperature of liquid granite at a given depth
    return 900 - 40 * sqrt(depth)

def contact(layers, intrusion):
    if intrusion is None:
        return layers

    top, bottom = intrusion

    # use the center of the intrusion to determine temperature
    temp = intrusiontemperature(float(top + bottom)/2)

    # assume the entire intrusion is constant temperature (and doesn't transform)
    # and the temperature drops linearly above and below, sloping to 0 (close
    # enough at the depths of intrusions) over the same distance as the intrusion's thickness

    thickness = bottom - top
    m = temp/thickness

    #                     _________
    # temp              /|         |\
    #                 /  |         |  \
    #      _________/    |         |    \__________
    #     |        |     |         |    |
    #     0       top -  top   bottom  bottom +
    #           thickness             thickness
    #
    #                      depth

    # gradient function above
    # t = m(d - (top - thickness))

    # gradient function below
    # t = -m(d - (bottom + thickness))

    d0 = max(0, top - thickness)
    facies = [(d0, IDENTITY)]

    # approaching intrusion from above
    for t, f in hightemp:
        # find the depth for the transition temperature
        d = t/m + (top - thickness) if not isinf(t) else float('inf')
        if d > top:
            facies.append((top, f))
            break
        if d > top - thickness:
            facies.append((d, f))

    # intrusion stays the same
    facies.append((bottom, IDENTITY))

    # away from intrusion below
    for i in reversed(range(len(hightemp)-1)):
        t = hightemp[i][0]
        f = hightemp[i+1][1]
        # find the depth for the transition temperature
        d = -t/m + bottom + thickness if not isinf(t) else float('inf')
        if d < bottom:
            continue
        if d < bottom + thickness:
            facies.append((d, f))

    facies.append((float('inf'), IDENTITY))

    i = 0
    while i < len(facies) - 1:
        if any([facies[i][n] == facies[i+1][n] for n in 0,1]):
            facies.pop(i)
        else:
            i += 1

    return transform(layers, facies)
