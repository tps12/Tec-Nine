from math import sin, cos, pi, atan2, sqrt

class Tile(object):
    MAX_HEIGHT = 10
    MAX_THICKNESS = 75

    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

        cos_lat = cos(self.lat * pi/180)
        self.vector = (cos_lat * cos(self.lon * pi/180),
                       cos_lat * sin(self.lon * pi/180),
                       sin(self.lat * pi/180))

        self.emptyocean()

    def distance(self, other):
        lat1, lon1 = [c * pi/180 for c in self.lat, self.lon]
        lat2, lon2 = [c * pi/180 for c in other.lat, other.lon]

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        return 2 * atan2(sqrt(a), sqrt(1-a))

    def limit(self):
        self.elevation = min(self.MAX_HEIGHT, self.elevation)
        self.thickness = min(self.MAX_THICKNESS, self.thickness)

    def averagesources(self, elevations, thicknesses, groupcount):
        self.elevation = float(sum(elevations))/len(elevations)
        self.thickness = float(sum(thicknesses))*groupcount/len(thicknesses)
        self.limit()

    def build(self, amount):
        self.elevation += amount
        self.thickness += 2 * amount
        self.limit()

    def depositnew(self, materials):
        amount = sum([m.amount for m in materials])
        self.elevation += amount
        self.thickness += amount + 5

    def depositexisting(self, materials):
        amount = sum([m.amount for m in materials])
        self.elevation += amount
        self.thickness += amount
        self.limit()

    def emptyland(self):
        self.elevation = 1
        self.thickness = 10

    def emptyocean(self):
        self.elevation = 0
        self.thickness = 5

    def __repr__(self):
        return 'Tile({0}, {1})'.format(self.lat, self.lon)
