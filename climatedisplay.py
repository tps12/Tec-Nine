from math import sin, cos, pi

from PySide.QtGui import QColor, QImage, QPainter, QWidget, QSizePolicy

from projection import *

class ClimateDisplay(QWidget):
    _projections = [mercator, sinusoidal, flat]   

    def __init__(self, sim):
        QWidget.__init__(self)
        self._sim = sim
        self._screen = None
        self._rotate = 0
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

    def invalidate(self):
        self._dirty = True

    colors = {
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

    def tilecolor(self, tile):
        h, k = tile.value, tile.climate

        if h > 0:
            color = self.colors[k[0]][k[1]]
        else:
            color = 0, 0, 0

        return QColor(*color)
    
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
