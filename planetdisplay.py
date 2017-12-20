from math import sin, cos, pi

from PySide.QtCore import Qt
from PySide.QtGui import QColor, QGridLayout, QImage, QPainter, QWidget, QSizePolicy

import color
import koeppencolor
from sphereview import SphereView

def redbluescale(v):
    r = 255 - 255 * v 
    b = 255 * v
    return r, 0, b

def climatecolor(tile):
    h, c = tile.elevation, tile.climate

    if c == None:
        return (255,255,255)

    k = c.koeppen

    if h > 0:
        color = koeppencolor.values[k[0]][k[1]]
    else:
        color = 0, 0, 0
    return color

def thicknesscolor(tile):
    h = tile.thickness

    if h > 0:
        value = int(128 + 1.69 * h)
        color = (value, value, value)
    else:
        color = (0, 0, 0)
    return color

def subductioncolor(tile):
    h = tile.elevation

    if h > 0:
        value = int(128 + 12.5 * h)
        s = tile.subduction
        if s > 0:
            r = value + (s/10.0) * (255 - value)
            color = (255, value, value)
        else:
            color = (value, value, value)
    else:
        color = (0, 0, 0)
    return color

def rockcolor(tile):
    h = tile.elevation

    if h > 0:
        value = int(128 + 12.5 * h)
        try:
            rocktype = tile.layers[-1].rock['type']
        except TypeError:
            rocktype = tile.layers[-1].rock
        if rocktype == 'I':
            color = (255, value, value)
        elif rocktype == 'S':
            color = (value, value, 255)
        else:
            color = (value, 255, value)
    else:
        color = (0, 0, 0)
    return color

def mountaincolor(tile):
    c = color.elevation(tile)
    return int(c[0] + tile.mountainosity * (255-c[0])), c[1], c[2]

class PlanetDisplay(QWidget):
    dt = 0.01

    _colorfunctions = [climatecolor, color.value, color.elevation, mountaincolor, rockcolor, subductioncolor, thicknesscolor]
    
    def __init__(self, sim, selecthandler):
        QWidget.__init__(self)
        self._sim = sim
        self._screen = None
        self._rotate = 0
        self._aspect = self._colorfunctions.index(color.elevation)
        self._select = selecthandler
        self.selected = None
        self.setLayout(QGridLayout())
        self.invalidate()

    @property
    def rotate(self):
        return self._rotate

    @rotate.setter
    def rotate(self, value):
        self._rotate = value
        self._screen.rotate(self._rotate)

    @property
    def aspect(self):
        return self._aspect

    @aspect.setter
    def aspect(self, value):
        self._aspect = value
        self.invalidate()

    def tilecolor(self, tile):
        return self._colorfunctions[self._aspect](tile)
   
    def select(self, x, y, z):
        self.selected = self._sim.nearest((z,-x,y)) if abs(z) < 2 else None
        self._select(self.selected)

    def invalidate(self):
        if self._screen is None:
            self._screen = SphereView(self._sim.grid.faces, self)
            self._screen.clicked.connect(self.select)
        self._screen.usecolors({ v: self.tilecolor(t) for (v, t) in self._sim.tiles.items() })
        self._screen.rotate(self._rotate)
        self.layout().addWidget(self._screen)
