from cPickle import load
from math import pi, cos

from adjacency import *
from climatemethod import climate
from earth import Earth
from tile import *

class ClimateSimulation(object):
    EXTENSION = '.tec9'

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

        c = climate(self.tiles, self.adj, seasons, self.cells, self.spin, self.tilt, self.temprange)
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
            t.value = earth.sample(t.lat, t.lon) / 900.0
            if t.value < 0:
                t.value = 0
        self.classify()

    def setdata(self, data):
        self.tiles = data['tiles']

    def load(self, filename):
        with open(filename, 'r') as f:
            self.setdata(load(f))
        self.classify()
