from math import sin, cos, pi

from PySide.QtGui import QColor, QGridLayout, QImage, QPainter, QWidget, QSizePolicy

from sphereview import SphereView

class SplitDisplay(QWidget):
    def __init__(self, sim):
        QWidget.__init__(self)
        self._sim = sim
        self._screen = None
        self._rotate = 0
        self._time = 2
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
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        self._time = value
        self.invalidate()

    def tilecolor(self, tile):
        h = tile.layers[0].rock if len(tile.layers) > 0 else None

        if h is not None:
            r = g = b = 128
            if h == 'R':
                if self._time > 0:
                    r = 255
            elif h == 'B':
                if self._time > 1:
                    b = 255
            color = (r, g, b)
        else:
            color = (255, 255, 255)
        return color

    def invalidate(self):
        if self._screen is None:
            self._screen = SphereView(self._sim.grid, self)
        self._screen.usecolors({ v: self.tilecolor(t) for (v, t) in self._sim.tiles.iteritems() })
        self._screen.rotate(self._rotate)
        self.layout().addWidget(self._screen)
