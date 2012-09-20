from PySide.QtCore import Qt
from PySide.QtGui import QImage

class Sinusoidal(object):
    @staticmethod
    def project(screen, size, tiles, rotate, tilecolor, backcolor = None):
        res = max([len(r) for r in tiles]), len(tiles)
        template = QImage(size[0]/res[0], size[1]/res[1], QImage.Format_RGB32)

        for y in range(res[1]):
            for x in range(len(tiles[y])):
                block = template.copy()

                r = rotate
                o = r * len(tiles[y])/360

                xo = x + o
                if xo > len(tiles[y])-1:
                    xo -= len(tiles[y])
                elif xo < 0:
                    xo += len(tiles[y])

                block.fill(tilecolor(tiles[y][xo]).rgb())
               
                screen.drawImage((x + (res[0] - len(tiles[y]))/2)*block.width(), y*block.height(), block)

    @staticmethod
    def unproject(size, tiles, rotate, pos):
        mx, my = pos

        res = max([len(r) for r in tiles]), len(tiles)

        y = my / (size[1]/res[1])
        x = mx / (size[0]/res[0]) - (res[0] - len(tiles[y]))/2

        r = rotate
        o = r * len(tiles[y])/360

        xo = x + o
        if xo > len(tiles[y])-1:
            xo -= len(tiles[y])
        elif xo < 0:
            xo += len(tiles[y])

        return xo, y

class Mercator(object):
    @staticmethod
    def project(screen, size, tiles, rotate, tilecolor, backcolor = None):
        res = len(tiles)
        template = QImage(size[0]/res, size[1]/res, QImage.Format_RGB32)

        for y in range(res):
            for x in range(res):
                block = template.copy()

                r = rotate
                o = r * res/360
                xo = (x + o) * len(tiles[y])/res

                if xo > len(tiles[y])-1:
                    xo -= len(tiles[y])
                elif xo < 0:
                    xo += len(tiles[y])

                block.fill(tilecolor(tiles[y][xo]).rgb())

                screen.drawImage(x*block.width(), y*block.height(), block)

    @staticmethod
    def unproject(size, tiles, rotate, pos):
        mx, my = pos

        res = len(tiles)

        y = my / (size[1]/res)
        x = mx / (size[0]/res)

        r = rotate
        o = r * res/360
        xo = (x + o) * len(tiles[y])/res

        if xo > len(tiles[y])-1:
            xo -= len(tiles[y])
        elif xo < 0:
            xo += len(tiles[y])

        return xo, y

class Flat(object):
    @staticmethod
    def project(screen, size, tiles, rotate, tilecolor, backcolor = None):
        backcolor = Qt.white if backcolor is None else backcolor

        res = len(tiles)
        template = QImage(size[0]/res, 2*size[1]/res, QImage.Format_RGB32)

        screen.setBrush(backcolor)
        screen.drawEllipse(0, 0, res * template.width()/2, res * template.height()/2)
        screen.drawEllipse(res * template.width()/2, 0, res * template.width()/2, res * template.height()/2)

        for y in range(res):
            r = rotate
            o = (r + 90) * len(tiles[y])/360

            # draw each hemisphere from outside to center
            sections = [[] for s in range(4)]
            i = 0
            while i < len(tiles[y]) and tiles[y][i].vector[0] < 0:
                sections[0].append(i)
                i += 1
            while i < len(tiles[y]) and tiles[y][i].vector[0] > tiles[y][i-1].vector[0]:
                sections[1].append(i)
                i += 1
            while i < len(tiles[y]) and tiles[y][i].vector[0] > 0:
                sections[2].append(i)
                i += 1
            while i < len(tiles[y]):
                sections[3].append(i)
                i += 1
                
            for x in sections[0] + list(reversed(sections[3])) + sections[2] + list(reversed(sections[1])):
                block = template.copy()

                xo = x + o
                if xo > len(tiles[y])-1:
                    xo -= len(tiles[y])
                elif xo < 0:
                    xo += len(tiles[y])

                v = tiles[y][x].vector
                sx, sy = [(v[i+1]+1)/2 for i in range(2)]
                sx = 1 + (sx if v[0] > 0 else -sx)

                block.fill(tilecolor(tiles[y][xo]).rgb())

                screen.drawImage(sx*res*block.width()/2, sy*res*block.height()/2, block)

    @staticmethod
    def unproject(size, tiles, rotate, pos):
        return None
