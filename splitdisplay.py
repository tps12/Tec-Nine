from math import sin, cos, pi

from PySide.QtGui import QColor, QImage, QPainter, QWidget, QSizePolicy

class SplitDisplay(QWidget):
    
    PROJECT_FLAT = 0
    PROJECT_MERC = 1
    PROJECT_SINE = 2

    def __init__(self, sim):
        QWidget.__init__(self)
        self._sim = sim
        self._screen = None
        self._rotate = 0
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
                        h = self._sim.tiles[y][xo].value

                        if h > 0:
                            r = g = b = 128
                            if h == 2:
                                r = 255
                            elif h == 3:
                                b = 255
                            color = (r, g, b)
                        else:
                            color = (255, 255, 255)
                        block.fill(QColor(*color).rgb())
                       
                        screen.drawImage((x + (res[0] - len(self._sim.tiles[y]))/2)*block.width(),
                                         y*block.height(), block)
            elif self._projection == self.PROJECT_FLAT:
                res = len(self._sim.tiles)
                template = QImage(size[0]/(2*res), size[1]/res, QImage.Format_RGB32)

                r2 = res*res/4
                for y in range(res):
                    for x in range(res):
                        if (x-res/2)**2 + (y-res/2)**2 <= r2:
                            for xh in x, x + res:
                                block = template.copy()

                                r = self.rotate
                                o = r * (2*res)/360
                                xo = (xh + o) * len(self._sim.tiles[y])/(2*res)

                                if xo > len(self._sim.tiles[y])-1:
                                    xo -= len(self._sim.tiles[y])
                                elif xo < 0:
                                    xo += len(self._sim.tiles[y])
                                h = self._sim.tiles[y][xo].value

                                if h > 0:
                                    r = g = b = 128
                                    if h == 2:
                                        r = 255
                                    elif h == 3:
                                        b = 255
                                    color = (r, g, b)
                                else:
                                    color = (255, 255, 255)
                                block.fill(QColor(*color).rgb())

                                screen.drawImage(xh*block.width(), y*block.height(), block)
            else:
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
                        h = self._sim.tiles[y][xo].value

                        if h > 0:
                            r = g = b = 128
                            if h == 2:
                                r = 255
                            elif h == 3:
                                b = 255
                            color = (r, g, b)
                        else:
                            color = (255, 255, 255)
                        block.fill(QColor(*color).rgb())

                        screen.drawImage(x*block.width(), y*block.height(), block)

            screen.end()

            self._dirty = False

        surface.drawImage(0, 0, self._screen)
        surface.end()
