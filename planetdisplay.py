from math import sin, cos, pi

from PySide.QtGui import QColor, QImage, QPainter, QWidget, QSizePolicy

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

class PlanetDisplay(QWidget):
    dt = 0.01
    
    def __init__(self, sim):
        QWidget.__init__(self)
        self._sim = sim
        self._screen = None
        self._rotate = 0
        self.selected = None
        self.dirty = True

    @property
    def rotate(self):
        return self._rotate

    @rotate.setter
    def rotate(self, value):
        self._rotate = value
        self._dirty = True
    
    def mousePressEvent(self, e):
        mx, my = e.pos().toTuple()

        res = max([len(r) for r in self._sim.tiles]), len(self._sim.tiles)

        size = self._screen.size().toTuple()

        y = my / (size[1]/res[1])
        x = mx / (size[0]/res[0]) - (res[0] - len(self._sim.tiles[y]))/2

        r = self._rotate
        o = r * len(self._sim.tiles[y])/360

        xo = x + o
        if xo > len(self._sim.tiles[y])-1:
            xo -= len(self._sim.tiles[y])
        elif xo < 0:
            xo += len(self._sim.tiles[y])
        
        if 0 <= y < len(self._sim.tiles) and 0 <= xo < len(self._sim.tiles[y]):
            if self.selected == (xo,y):
                self.selected = None
            else:
                self.selected = (xo,y)
   
            self._dirty = True

            return True
    
    def paintEvent(self, e):
        surface = QPainter()
        surface.begin(self)
        
        if (self._sim.dirty or self._dirty or
            self._screen == None or self._screen.size() != surface.size()):
            self._screen = QImage(surface.device().width(), surface.device().height(),
                                  QImage.Format_RGB32)
            
            size = self._screen.width(), self._screen.height()
        
            self._screen.fill(QColor(0,0,0).rgb())

            screen = QPainter()
            screen.begin(self._screen)

            res = max([len(r) for r in self._sim.tiles]), len(self._sim.tiles)
            template = QImage(size[0]/res[0], size[1]/res[1],
                              QImage.Format_RGB32)

            for y in range(res[1]):
                for x in range(len(self._sim.tiles[y])):
                    block = template.copy()

                    r = self.rotate
                    o = r * len(self._sim.tiles[y])/360

                    xo = x + o
                    if xo > len(self._sim.tiles[y])-1:
                        xo -= len(self._sim.tiles[y])
                    elif xo < 0:
                        xo += len(self._sim.tiles[y])
                    h = self._sim.tiles[y][xo].value

                    if self.selected == (xo,y):
                        color = (255, 255, 0)
                    elif h > 0:
                        value = int(255 - 25 * h)
                        color = (value, value, value)
                    else:
                        color = (255, 255, 255)
                    block.fill(QColor(*color).rgb())
                   
                    screen.drawImage((x + (res[0] - len(self._sim.tiles[y]))/2)*block.width(),
                                     y*block.height(), block)
            screen.end()

            self._dirty = False

        surface.drawImage(0, 0, self._screen)
        surface.end()
