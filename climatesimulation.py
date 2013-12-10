from math import pi, cos

from adjacency import *
from climatemethod import climate
from earth import Earth
from planetdata import Data
from tile import *

class ClimateSimulation(object):
    spin = 1.0
    tilt = 23

    temprange = (-25.0, 50.0)
    
    def __init__(self, r):
        """Create a simulation for a planet of radius r km."""
        degrees = 2

        self.tiles = []
        for lat in range(-89, 91, degrees):
            r = cos(lat * pi/180)
            row = []
            d = 2 / r
            lon = d/2
            while lon <= 180:
                flat = float(lat)
                row = ([Tile(flat, -lon)] +
                       row +
                       [Tile(flat, lon)])
                lon += d
            self.tiles.append(row)

        self.adj = Adjacency(self.tiles)
        self.cells = 3

    def classify(self, seasons = None):
        seasons = [-1, -0.5, 0, 0.5, 1, 0.5, 0, -0.5] if seasons is None else seasons

        c = climate(self.tiles, self.adj, seasons, self.cells, self.spin, self.tilt, self.temprange, True, {})
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                self.tiles[y][x].climate = c[(x,y)].koeppen
    
    @property
    def cells(self):
        return self._cells

    @cells.setter
    def cells(self, value):
        self._cells = value
        self.classify()

    @property
    def earthavailable(self):
        return Earth.available()

    def earth(self):
        earth = Earth()
        for t in [t for lat in self.tiles for t in lat]:
            elevation = earth.sample(t.lat, t.lon) / 900.0
            if elevation < 0:
                elevation = 0
            t.bottom = -1
            t.layers = [Layer('S', elevation + 1)]
            t.limit()
        self.classify()

    def load(self, filename):
        data = Data.load(filename)
        self.tiles = data['tiles']
        self.classify()
