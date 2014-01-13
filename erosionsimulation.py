from math import pi, cos

from adjacency import *
from climatemethod import climate
from earth import Earth
from erodemethod import erode, Erosion
from planetdata import Data
from tile import *

class ErosionSimulation(object):
    cells = 3
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

        for t in [t for lat in self.tiles for t in lat]:
            t.eroding = Erosion()
            t.climate = None

        self.adj = Adjacency(self.tiles)

    def erode(self):
        seasons = [-1, -0.5, 0, 0.5, 1, 0.5, 0, -0.5]

        climatetiles = {}
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                climatetiles[(x,y)] = self.tiles[y][x]

        c = climate(climatetiles, self.adj, seasons, self.cells, self.spin, self.tilt, self.temprange, True, {})

        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                self.tiles[y][x].climate = c[(x,y)]['classification']

        erosion = erode(self.tiles, self.adj)

        for t in [t for lat in self.tiles for t in lat]:
            t.erode(erosion, 1.0)
            t.eroding = erosion[t]

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
            t.layers = [Layer({ 'type': 'S', 'toughness': 0.5 }, elevation + 1)]
            t.limit()
        self.erode()

    def load(self, filename):
        data = Data.load(filename)
        self.tiles = data['tiles']
        self.erode()
