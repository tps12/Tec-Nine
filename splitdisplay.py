from math import sin, cos, pi

from PySide.QtGui import QColor, QImage, QPainter, QWidget, QSizePolicy

from projection import *

class SplitDisplay(QWidget):
    _projections = [sinusoidal, mercator, flat]
    
    def __init__(self, sim):
        QWidget.__init__(self)
        self._sim = sim
        self._screen = None
        self._rotate = 0
        self._time = 2
        self._projection = 0
        self._dirty = True

    @property
    def projection(self):
        return self._projection

    @projection.setter
    def projection(self, value):
        self._projection = value
        self._dirty = True
    
    @property
    def rotate(self):
        return self._rotate

    @rotate.setter
    def rotate(self, value):
        self._rotate = value
        self._dirty = True

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        self._time = value
        self._dirty = True

    def tilecolor(self, tile):
        h = tile.value

        if h > 0:
            r = g = b = 128
            if h == 2:
                if self._time > 0:
                    r = 255
            elif h == 3:
                if self._time > 1:
                    b = 255
            color = (r, g, b)
        else:
            color = (255, 255, 255)
        return QColor(*color)

    def invalidate(self):
        self._dirty = True
    
    def paintEvent(self, e):
        surface = QPainter()
        surface.begin(self)
        
        if (self._dirty or self._screen == None or self._screen.size() != surface.device().size()):
            self._screen = QImage(surface.device().width(), surface.device().height(),
                                  QImage.Format_RGB32)
            
            size = self._screen.size().toTuple()
        
            self._screen.fill(QColor(0,0,0).rgb())

            screen = QPainter()
            screen.begin(self._screen)

            self._projections[self._projection](screen, size, self._sim.tiles, self.rotate, self.tilecolor)

            screen.end()

            self._dirty = False

        surface.drawImage(0, 0, self._screen)
        surface.end()
