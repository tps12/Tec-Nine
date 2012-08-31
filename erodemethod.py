class ErodedMaterial(object):
    def __init__(self, amount, source=None):
        self.amount = amount
        self.source = source

def erode(tiles, adjacency, climate):
    erosion = {}

    for t in [t for lat in tiles for t in lat]:
        erosion[t] = []

    # erode to lower adjacent tiles
    for i in range(len(tiles)):
        for j in range(len(tiles[i])):
            tile = tiles[i][j]
            if tile.elevation > 0:
                adj = adjacency[(j,i)]
                for (j2,i2) in adj:
                    other = tiles[i2][j2]
                    d = tile.elevation - other.elevation
                    if climate:
                        c = climate[(j,i)]
                        # glaciers erode a lot
                        if c.koeppen[0] == u'E':
                            pass
                        # everything else erodes according to precipitation
                        else:
                            d *= c.precipitation
                    if d > 0:
                        d /= len(adj)
                        erosion[tile].append(ErodedMaterial(-d))
                        erosion[other].append(ErodedMaterial(d, tile))

    return erosion
