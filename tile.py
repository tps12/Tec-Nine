from math import sin, cos, pi

class Tile(object):
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

        cos_lat = cos(self.lat * pi/180)
        self.vector = (cos_lat * cos(self.lon * pi/180),
                       cos_lat * sin(self.lon * pi/180),
                       sin(self.lat * pi/180))


        self.value = 0
