class ErosionEvent(object):
    def __init__(self, degree, destination):
        self.degree = degree
        self.destination = destination

class ErosionMaterial(object):
    def __init__(self, amount, substance):
        self.amount = amount
        self.substance = substance

class Erosion(object):
    def __init__(self):
        self.destinations = []
        self.materials = []
        self.sources = []

    def addmaterial(self, amount, substance):
        self.materials.append(ErosionMaterial(amount, substance))

# no longer exists; remains so tiles pickled pre-version 2 can be loaded
class ErodedMaterial(object):
    pass

def erode(tiles, adjacency):
    erosion = {}

    for t in [t for lat in tiles for t in lat]:
        erosion[t] = Erosion()

    # erode to lower adjacent tiles
    for i in range(len(tiles)):
        for j in range(len(tiles[i])):
            tile = tiles[i][j]
            if tile.elevation > 0:
                adj = adjacency[(j,i)]
                for (j2,i2) in adj:
                    other = tiles[i2][j2]
                    d = tile.elevation - other.elevation
                    c = tile.climate
                    if c is not None:
                        # glaciers erode a lot
                        if c.koeppen[0] == u'E':
                            pass
                        # everything else erodes according to precipitation
                        else:
                            d *= c.precipitation
                    if d > 0:
                        d /= len(adj)
                        erosion[tile].destinations.append(ErosionEvent(d, other))
                        erosion[other].sources.append(tile)

    return erosion
