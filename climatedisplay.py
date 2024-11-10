from math import sin, cos, pi

from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtWidgets import QGridLayout, QWidget, QSizePolicy

from koeppencolor import values as koeppenvalues
from sphereview import SphereView

def koeppencolor(tile):
    h, k = tile.elevation, tile.climate['koeppen']

    if h > 0:
        color = koeppenvalues[k[0]][k[1]]
    else:
        color = 0, 0, 0

    return color

def seasonindex(s, ss):
  return ss[int(round((len(ss)-1) * s/100.0))]

def precipcolor(tile, season):
    h, s = tile.elevation, tile.climate['precipitation']

    if h > 0:
        value = 128 + 127 * seasonindex(season, s)
        color = (value, value, value)
    else:
        color = 0, 0, 0

    return color

def tempcolor(tile, season):
    h, s = tile.elevation, seasonindex(season, tile.climate['temperature'])

    if h > 0:
        g = 0
        r = 255 * (1 if s >= 0.5 else s/0.5)
        b = 255 * (1 if s < 0.5 else (1-s)/0.5)
    else:
        r = g = b = 0

    return r, g, b

def suncolor(tile, season):
    h, s = tile.elevation, seasonindex(season, tile.climate['insolation'])
    if h > 0:
        r = 255
        g = 255 * (1 if s >= 0.5 else s/0.5)
        b = 255 * (0 if s < 0.5 else (s-0.5)/0.5)
    else:
        r = g = b = 0

    return r, g, b

class ClimateDisplay(QWidget):
    _attributes = [
        { 'name': name, 'function': function, 'seasonal': seasonal }
        for name, function, seasonal in [
            ('koeppen', koeppencolor, False),
            ('insolation', suncolor, True),
            ('precipitation', precipcolor, True),
            ('temperature', tempcolor, True)]]

    def __init__(self, sim):
        QWidget.__init__(self)
        self._sim = sim
        self._screen = None
        self._rotate = 0
        self.shownattribute = 0
        self.season = 0
        self.glaciation = 0.5
        self.setLayout(QGridLayout())
        self.invalidate()

    @property
    def rotate(self):
        return self._rotate

    @rotate.setter
    def rotate(self, value):
        self._rotate = value
        self._screen.rotate(self._rotate)

    def invalidate(self):
        if self._screen is None:
            self._screen = SphereView(self._sim.grid.faces, self)
        attribute = self._attributes[self.shownattribute]
        if attribute['seasonal']:
            fn = lambda t: attribute['function'](t, self.season)
        else:
            fn = attribute['function']
        self._screen.usecolors({ v: fn(t) for (v, t) in self._sim.tiles.items() })
        self._screen.rotate(self._rotate)
        self.layout().addWidget(self._screen)
