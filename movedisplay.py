from math import sin, cos, pi

from PySide.QtGui import QColor, QGridLayout, QImage, QPainter, QWidget, QSizePolicy

from sphereview import SphereView

class MoveDisplay(QWidget):
    def __init__(self, sim):
        QWidget.__init__(self)
        self._sim = sim
        self._screen = None
        self._rotate = 0
        self._trail = True
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
    def trail(self):
        return self._trail

    @trail.setter
    def trail(self, value):
        self._trail = value

    def tilecolor(self, tile):
        h = tile.layers[0].rock if len(tile.layers) > 0 else None

        if h == 'T':
            color = (128, 128, 128)
        elif h == 'M' and self._trail:
            color = (192, 192, 192)
        else:
            color = (255, 255, 255)
        return color

    def invalidate(self):
        if self._screen is not None:
            self._screen.deleteLater()
        self._screen = SphereView(
                self._sim.grid,
                { v: self.tilecolor(t) for (v, t) in self._sim.tiles.iteritems() },
                self)
        self._screen.rotate(self._rotate)
        self.layout().addWidget(self._screen)
