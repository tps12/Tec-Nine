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

def value(tile):
    h, c = tile.elevation, tile.climate

    l = c.life if c else 0
    k = c.koeppen if c else None

    if h > 0:
        try:
            f = tile.layers[-1].rock['felsity']
        except KeyError:
            f = 0
        rockcolor = (128, 64 + 64 * f, 128 * f)

        if k:
            if k[0] == u'E':
                color = (255,255,255)
            else:
                lifecolor = (0,l*255,0)
                color = tuple([(r+l)/2 for r,l in zip(rockcolor, lifecolor)])
        else:
            color = rockcolor
    else:
        color = (0, 0, 128)

    return color
