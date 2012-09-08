from cPickle import load
from math import pi, cos

from adjacency import *
from climatemethod import climate
from earth import Earth
from erodemethod import erode, Erosion
from tile import *

class ErosionSimulation(object):
    EXTENSION = '.tec9'

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
        
        self._climate = False

    def erode(self):
        seasons = [-1, -0.5, 0, 0.5, 1, 0.5, 0, -0.5]

        if self.climate:
            c = climate(self.tiles, self.adj, seasons, self.cells, self.spin, self.tilt, self.temprange)
        else:
            c = None

        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                self.tiles[y][x].climate = c[(x,y)] if c is not None else None

        erosion = erode(self.tiles, self.adj)

        for t in [t for lat in self.tiles for t in lat]:
            t.erode(erosion)
            t.eroding = erosion[t]

    @property
    def climate(self):
        return self._climate

    @climate.setter
    def climate(self, value):
        if self._climate != value:
            self._climate = value
            self.erode()

    @property
    def earthavailable(self):
        return Earth.available()

    def earth(self):
        earth = Earth()
        for t in [t for lat in self.tiles for t in lat]:
            t.elevation = earth.sample(t.lat, t.lon) / 900.0
            if t.elevation < 0:
                t.elevation = 0
        self.erode()

    def setdata(self, data):
        self.tiles = data['tiles']
        if 'version' not in data:
            for t in [t for lat in self.tiles for t in lat]:
                t.elevation = t.value
                del t.value
            data['version'] = 0
        if data['version'] == 0:
            for t in [t for lat in self.tiles for t in lat]:
                t.thickness = 10 if t.elevation > 0 else 5
            data['version'] = 1

        for t in [t for lat in self.tiles for t in lat]:
            t.eroding = []
            t.overlapping = []

    def load(self, filename):
        with open(filename, 'r') as f:
            self.setdata(load(f))
        self.erode()
