class ErosionEvent(object):
    def __init__(self, degree, destination):
        self.degree = degree
        self.destination = destination

class ErosionMaterial(object):
    def __init__(self, amount, total, substance):
        self.amount = amount
        self.total = total
        self.substance = substance

class Erosion(object):
    def __init__(self):
        self.destinations = []
        self.materials = []
        self.sources = []

    def addmaterial(self, amount, total, substance):
        self.materials.append(ErosionMaterial(amount, total, substance))

def erode(tiles, adjacency):
    erosion = {}

    for t in tiles.itervalues():
        erosion[t] = Erosion()

    # erode to lower adjacent tiles
    for (v, tile) in tiles.iteritems():
        if tile.elevation > 0:
            c = tile.climate
            d = (tile.elevation/10.0) * c.precipitation * (1 - c.temperature)
            adj = adjacency[v]
            for v2 in adj:
                other = tiles[v2]
                erosion[tile].destinations.append(ErosionEvent(d, other))
                erosion[other].sources.append(tile)

    return erosion
