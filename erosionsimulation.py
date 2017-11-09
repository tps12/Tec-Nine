from math import pi, cos

from grid import Grid
from hexadjacency import *
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
        grid = Grid()
        while grid.size < 6:
            grid = Grid(grid)
            grid.populate()
        self._grid = grid

        self.tiles = {}
        for v in self._grid.faces:
            x, y, z = v
            lat = 180/pi * atan2(z, sqrt(x*x + y*y))
            lon = 180/pi * atan2(y, x)
            self.tiles[v] = Tile(lat, lon)

        for t in self.tiles.itervalues():
            t.eroding = Erosion()
            t.climate = t.seasons = None

        self.adj = Adjacency(self._grid)

    @property
    def grid(self):
        return self._grid

    def erode(self):
        seasons = [-1, -0.5, 0, 0.5, 1, 0.5, 0, -0.5]

        c = climate(self.tiles, self.adj, seasons, self.cells, self.spin, self.tilt, self.temprange, True, {})

        for v, tiles in self.tiles.iteritems():
            self.tiles[v].climate = c[v]['classification']
            self.tiles[v].seasons = c[v]['seasons']

        erosion = erode(self.tiles, self.adj)

        for t in self.tiles.itervalues():
            t.erode(erosion, 1.0)
            t.eroding = erosion[t]

    @property
    def earthavailable(self):
        return Earth.available()

    def earth(self):
        earth = Earth()
        for t in self.tiles.itervalues():
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
