from math import pi, cos

from grid import Grid
from hexadjacency import *
from climatemethod import climate
from earth import Earth
from planetdata import Data
from tile import *

class ClimateSimulation(object):
    spin = 1.0
    tilt = 23

    mean_temprange = (-25.0, 50.0)
    
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


        self.adj = Adjacency(self._grid)
        self.cells = 3
        self.glaciation = 0.5

    @property
    def grid(self):
        return self._grid

    def classify(self, seasons = None):
        seasons = [-1, -0.5, 0, 0.5, 1, 0.5, 0, -0.5] if seasons is None else seasons
        self.seasoncount = len(seasons)
        c = climate(self.tiles, self.adj, seasons, self.cells, self.spin, self.tilt, self.temprange, self.glaciation, True, {})
        for v, tile in self.tiles.items():
            tile.climate = {
                'koeppen': c[v]['classification'].koeppen,
                'insolation': [s['insolation'] for s in c[v]['seasons']],
                'precipitation': [s['precipitation'] for s in c[v]['seasons']],
                'temperature': [s['temperature'] for s in c[v]['seasons']] }
    
    @property
    def cells(self):
        return self._cells

    @cells.setter
    def cells(self, value):
        self._cells = value
        self.classify()

    @property
    def glaciation(self):
      return self._glaciation if hasattr(self, '_glaciation') else 0.5

    @glaciation.setter
    def glaciation(self, value):
        self._glaciation = value
        self.classify()

    @property
    def temprange(self):
      dtemp = 5 * (self.glaciation / 0.5)
      return (self.mean_temprange[0] + dtemp, self.mean_temprange[1] + dtemp)

    @property
    def earthavailable(self):
        return Earth.available()

    def earth(self):
        earth = Earth()
        for t in self.tiles.values():
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
