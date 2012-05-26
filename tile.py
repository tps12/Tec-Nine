from math import sin, cos, pi, atan2, sqrt

class Tile(object):
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

        cos_lat = cos(self.lat * pi/180)
        self.vector = (cos_lat * cos(self.lon * pi/180),
                       cos_lat * sin(self.lon * pi/180),
                       sin(self.lat * pi/180))


        self.value = 0

    def distance(self, other):
        lat1, lon1 = [c * pi/180 for c in self.lat, self.lon]
        lat2, lon2 = [c * pi/180 for c in other.lat, other.lon]

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        return 2 * atan2(sqrt(a), sqrt(1-a))

    def __repr__(self):
        return 'Tile({0}, {1})'.format(self.lat, self.lon)
