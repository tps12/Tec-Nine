def extrusive(silica):
    if silica > 0.63:
        name = 'rhyolite'
    elif silica > 0.52:
        name = 'dacite'
    else:
        name = 'basalt'

    return { 'type': 'I', 'name': name, 'felsity': silica, 'toughness': silica }

def intrusive(silica):
    if silica > 0.63:
        name = 'granite'
    elif silica > 0.52:
        name = 'andesite'
    else:
        name = 'gabbro'

    return { 'type': 'I', 'name': name, 'felsity': silica, 'toughness': silica }
