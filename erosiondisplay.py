from math import sin, cos, pi

from PySide.QtGui import QColor, QImage, QPainter, QWidget, QSizePolicy

from projection import *

class ErosionDisplay(QWidget):
    _projections = [mercator, sinusoidal, flat]   

    def __init__(self, sim):
        QWidget.__init__(self)
        self._sim = sim
        self._screen = None
        self._rotate = 0
        self._projection = 0
        self._lost = self._gained = True
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
    def lost(self):
        return self._lost

    @lost.setter
    def lost(self, value):
        if self._lost != value:
            self._lost = value
            self._dirty = True

    @property
    def gained(self):
        return self._gained

    @gained.setter
    def gained(self, value):
        if self._gained != value:
            self._gained = value
            self._dirty = True

    def invalidate(self):
        self._dirty = True

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

        return QColor(r, g, b)
          
    def paintEvent(self, e):
        surface = QPainter()
        surface.begin(self)
        
        if (self._dirty or self._screen == None or self._screen.size() != surface.device().size()):
            self._screen = QImage(surface.device().width(), surface.device().height(),
                                  QImage.Format_RGB32)
            
            size = self._screen.size().toTuple()
        
            self._screen.fill(QColor(255,255,255).rgb())

            screen = QPainter()
            screen.begin(self._screen)

            self._projections[self._projection](screen, size, self._sim.tiles, self.rotate, self.tilecolor)

            screen.end()

            self._dirty = False

        surface.drawImage(0, 0, self._screen)
        surface.end()
