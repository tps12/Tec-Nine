def elevationcolor(h):
    if h > 0:
        value = int(128 + 12.5 * h)
        color = (value, value, value)
    else:
        color = (0, 0, 0)
    return color

def elevation(tile):
    return elevationcolor(tile.elevation)

def warm(v):
    m = 510
    r = 255
    g = v * m if v < 0.5 else 255
    b = 0 if v < 0.5 else m * (v - 0.5)
    return r, g, b

def rock(tile):
    if tile.elevation <= 0:
        return None
    r = tile.layers[-1].rock
    f = r['felsity'] if 'felsity' in r else 0
    return (128, 64 + 64 * f, 128 * f)

def snow(tile):
    if tile.elevation > 0 and tile.climate and tile.climate.koeppen[0] == u'E':
        return (255,255,255)
    return None

def value(tile):
    rockcolor = rock(tile)
    if not rockcolor:
        return (0, 0, 128)
    snowcolor = snow(tile)
    if snowcolor:
        return snowcolor

    c = tile.climate

    l = c.life if c else 0
    k = c.koeppen if c else None

    if k:
        lifecolor = (0,l*255,0)
        color = tuple([(r+l)/2 for r,l in zip(rockcolor, lifecolor)])
    else:
        color = rockcolor

    return color
