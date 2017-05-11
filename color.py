def value(tile):
    h, c = tile.elevation, tile.climate

    l = c.life if c else 0
    k = c.koeppen if c else None

    colors = {
        u'A' : {
            u'f' : (0,96,48),
            u'm' : (0,168,84),
            u'w' : (0,255,128) },
        u'B' : {
            u'S' : (208,208,208),
            u'W' : None },
        u'C' : {
            u'f' : (0,96,0),
            u's' : (0,168,0),
            u'w' : (0,255,0) },
        u'D' : {
            u'f' : (48,96,48),
            u's' : (84,168,84),
            u'w' : (128,255,128) },
        u'E' : {
            u'F' : (255, 255, 255),
            u'T' : (255, 255, 255) }
    }

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
