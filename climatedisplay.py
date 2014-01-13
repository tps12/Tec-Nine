from math import sin, cos, pi

from PySide.QtGui import QColor, QGridLayout, QImage, QPainter, QWidget, QSizePolicy

from sphereview import SphereView

koeppencolors = {
    u'A' : {
        u'f' : (0,0,255),
        u'm' : (0,63,255),
        u'w' : (0,127,255) },
    u'B' : {
        u'S' : (255,127,0),
        u'W' : (255,0,0) },
    u'C' : {
        u'f' : (0,255,0),
        u's' : (255,255,0),
        u'w' : (127,255,0) },
    u'D' : {
        u'f' : (0,255,255),
        u's' : (255,0,255),
        u'w' : (127,127,255) },
    u'E' : {
        u'F' : (127,127,127),
        u'T' : (191,191,191) }
}

def koeppencolor(tile):
    h, k = tile.elevation, tile.climate['koeppen']

    if h > 0:
        color = koeppencolors[k[0]][k[1]]
    else:
        color = 0, 0, 0

    return color

def precipcolor(tile, season):
    h, s = tile.elevation, tile.climate['precipitation']

    if h > 0:
        value = 128 + 127 * s[season]
        color = (value, value, value)
    else:
        color = 0, 0, 0

    return color

def tempcolor(tile, season):
    h, s = tile.elevation, tile.climate['temperature'][season]

    if h > 0:
        g = 0
        r = 255 * (1 if s >= 0.5 else s/0.5)
        b = 255 * (1 if s < 0.5 else (1-s)/0.5)
    else:
        r = g = b = 0

    return r, g, b

def suncolor(tile, season):
    h, s = tile.elevation, tile.climate['insolation'][season]
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
        if self._screen is not None:
            self._screen.deleteLater()
        attribute = self._attributes[self.shownattribute]
        if attribute['seasonal']:
            fn = lambda t: attribute['function'](t, self.season)
        else:
            fn = attribute['function']
        self._screen = SphereView(
            self._sim.grid,
            { v: fn(t) for (v, t) in self._sim.tiles.iteritems() },
            self)
        self._screen.rotate(self._rotate)
        self.layout().addWidget(self._screen)
