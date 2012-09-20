from math import sin, cos, pi

from PySide.QtCore import Qt
from PySide.QtGui import QColor, QImage, QPainter, QWidget, QSizePolicy

from projection import *

def redbluescale(v):
    r = 255 - 255 * v 
    b = 255 * v
    return r, 0, b

def colorscale(v):
    m = 1275
    r = (255 - m * v if v < 0.2 else
         0 if v < 0.6 else
         m * (v - 0.6) if v < 0.8 else
         255)
    g = (0 if v < 0.2 else
         m * (v - 0.2) if v < 0.4 else
         255 if v < 0.8 else
         255 - m * (v - 0.8))
    b = (255 if v < 0.4 else
         255 - m * (v - 0.4) if v < 0.6 else
         0)
    return r, g, b

def warmscale(v):
    m = 510
    r = 255
    g = v * m if v < 0.5 else 255
    b = 0 if v < 0.5 else m * (v - 0.5)
    return r, g, b

def coolscale(v):
    m = 1020
    r = 255 - m * v if v < 0.25 else 0
    g = (255 if v < 0.75 else
         255 - m * (v - 0.75))
    b = (255 - m * v if v < 0.25 else
         m * (v - 0.25) if v < 0.5 else
         255)
    return r, g, b


def climatecolor(tile):
    h, c = tile.elevation, tile.climate

    if c == None:
        return (255,255,255)

    k = c.koeppen

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

    if h > 0:
        color = colors[k[0]][k[1]]
    else:
        color = 0, 0, 0
    return color

def elevationcolor(tile):
    h = tile.elevation

    if h > 0:
        value = int(128 + 12.5 * h)
        color = (value, value, value)
    else:
        color = (0, 0, 0)
    return color

def thicknesscolor(tile):
    h = tile.thickness

    if h > 0:
        value = int(128 + 1.69 * h)
        color = (value, value, value)
    else:
        color = (0, 0, 0)
    return color

def rockcolor(tile):
    h = tile.elevation

    if h > 0:
        value = int(128 + 12.5 * h)
        if tile.layers[-1].rock == 'I':
            color = (255, value, value)
        elif tile.layers[-1].rock == 'S':
            color = (value, value, 255)
        else:
            color = (value, 255, value)
    else:
        color = (0, 0, 0)
    return color

class PlanetDisplay(QWidget):
    dt = 0.01

    _projections = [Mercator, Sinusoidal, Flat]

    _colorfunctions = [climatecolor, elevationcolor, rockcolor, thicknesscolor]
    
    def __init__(self, sim, selecthandler):
        QWidget.__init__(self)
        self._sim = sim
        self._screen = None
        self._rotate = 0
        self._projection = 0
        self._aspect = self._colorfunctions.index(elevationcolor)
        self._select = selecthandler
        self.selected = None
        self.dirty = True

    @property
    def rotate(self):
        return self._rotate

    @rotate.setter
    def rotate(self, value):
        self._rotate = value
        self._dirty = True
    
    @property
    def projection(self):
        return self._projection

    @projection.setter
    def projection(self, value):
        self._projection = value
        self._dirty = True

    @property
    def aspect(self):
        return self._aspect

    @aspect.setter
    def aspect(self, value):
        self._aspect = value
        self._dirty = True
    
    def mousePressEvent(self, e):
        pos = e.pos().toTuple()
        size = self._screen.size().toTuple()

        self._select(self._projections[self._projection].unproject(size, self._sim.tiles, self.rotate, pos))

    def tilecolor(self, tile):
        return QColor(*self._colorfunctions[self._aspect](tile))
   
    def paintEvent(self, e):
        surface = QPainter()
        surface.begin(self)
        
        if (self._sim.dirty or self._dirty or
            self._screen == None or self._screen.size() != surface.device().size()):
            self._screen = QImage(surface.device().width(), surface.device().height(),
                                  QImage.Format_RGB32)
            
            size = self._screen.width(), self._screen.height()
        
            self._screen.fill(QColor(255,255,255).rgb())

            screen = QPainter()
            screen.begin(self._screen)

            self._projections[self._projection].project(screen, size, self._sim.tiles, self.rotate, self.tilecolor, Qt.black)

            screen.end()

            self._dirty = False

        surface.drawImage(0, 0, self._screen)
        surface.end()
