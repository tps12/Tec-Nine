from math import sin, cos, pi

from PySide.QtGui import QColor, QImage, QPainter, QWidget, QSizePolicy

class SplitDisplay(QWidget):
    
    PROJECT_MERC = 0
    PROJECT_SINE = 1
    PROJECT_FLAT = 2

    def __init__(self, sim):
        QWidget.__init__(self)
        self._sim = sim
        self._screen = None
        self._rotate = 0
        self._time = 2
        self._projection = self.PROJECT_SINE
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

    @staticmethod
    def tilecolor(tile, time):
        h = tile.value

        if h > 0:
            r = g = b = 128
            if h == 2:
                if time > 0:
                    r = 255
            elif h == 3:
                if time > 1:
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

            if self._projection == self.PROJECT_SINE:
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

                        block.fill(self.tilecolor(self._sim.tiles[y][xo], self._time).rgb())
                       
                        screen.drawImage((x + (res[0] - len(self._sim.tiles[y]))/2)*block.width(),
                                         y*block.height(), block)
            elif self._projection == self.PROJECT_MERC:
                res = len(self._sim.tiles)
                template = QImage(size[0]/res, size[1]/res, QImage.Format_RGB32)

                for y in range(res):
                    for x in range(res):
                        block = template.copy()

                        r = self.rotate
                        o = r * res/360
                        xo = (x + o) * len(self._sim.tiles[y])/res

                        if xo > len(self._sim.tiles[y])-1:
                            xo -= len(self._sim.tiles[y])
                        elif xo < 0:
                            xo += len(self._sim.tiles[y])

                        block.fill(self.tilecolor(self._sim.tiles[y][xo], self._time).rgb())
 
                        screen.drawImage(x*block.width(), y*block.height(), block)
            else:
                res = len(self._sim.tiles)
                template = QImage(size[0]/res/2, size[1]/res, QImage.Format_RGB32)

                for y in range(res):
                    r = self.rotate
                    o = (r + 90) * len(self._sim.tiles[y])/360
                    for x in range(len(self._sim.tiles[y])):
                        block = template.copy()

                        xo = x + o
                        if xo > len(self._sim.tiles[y])-1:
                            xo -= len(self._sim.tiles[y])
                        elif xo < 0:
                            xo += len(self._sim.tiles[y])

                        v = self._sim.tiles[y][x].vector
                        sx, sy = [(v[i+1]+1)/2 for i in range(2)]
                        sx = 1 + (sx if v[0] > 0 else -sx)

                        block.fill(self.tilecolor(self._sim.tiles[y][xo], self._time).rgb())

                        screen.drawImage(sx*res*block.width(), sy*res*block.height(), block)

            screen.end()

            self._dirty = False

        surface.drawImage(0, 0, self._screen)
        surface.end()
