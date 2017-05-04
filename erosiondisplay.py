from math import sin, cos, pi

from PySide.QtGui import QColor, QGridLayout, QImage, QPainter, QWidget, QSizePolicy

from sphereview import SphereView

class ErosionDisplay(QWidget):
    def __init__(self, sim):
        QWidget.__init__(self)
        self._sim = sim
        self._screen = None
        self._rotate = 0
        self._lost = self._gained = True
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
    def lost(self):
        return self._lost

    @lost.setter
    def lost(self, value):
        if self._lost != value:
            self._lost = value
            self.invalidate()

    @property
    def gained(self):
        return self._gained

    @gained.setter
    def gained(self, value):
        if self._gained != value:
            self._gained = value
            self.invalidate()

    def invalidate(self):
        if self._screen is None:
            self._screen = SphereView(self._sim.grid, self)
        self._screen.usecolors({ v: self.tilecolor(t) for (v, t) in self._sim.tiles.iteritems() })
        self._screen.rotate(self._rotate)
        self.layout().addWidget(self._screen)

    def tilecolor(self, tile):
        h = tile.elevation

        if h > 0:
            v = 128
            r = g = b = int(v + 12.5 * h)
        else:
            r = g = b = v = 0

        if self.lost:
            t = sum([d.degree for d in tile.eroding.destinations])
            r = v + abs(max(-5, t)) * 25.5 
            g = b = v

        if self.gained:
            t = sum([m.amount for m in tile.eroding.materials])
            g = v + abs(min(5, t)) * 25.5
            b = v
            if not self.lost:
                r = v

        return r, g, b
