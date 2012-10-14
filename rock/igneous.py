def extrusive(silica):
    if silica > 0.63:
        name = 'rhyolite'
    elif silica > 0.52:
        name = 'dacite'
    else:
        name = 'basalt'

    return { 'type': 'I', 'name': name, 'felsity': silica }
