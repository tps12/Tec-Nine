from PySide.QtGui import QImage

def sinusoidal(screen, size, tiles, rotate, tilecolor):
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

def mercator(screen, size, tiles, rotate, tilecolor):
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

def flat(screen, size, tiles, rotate, tilecolor):
        res = len(tiles)
        template = QImage(size[0]/res/2, size[1]/res, QImage.Format_RGB32)

        for y in range(res):
            r = rotate
            o = (r + 90) * len(tiles[y])/360
            for x in range(len(tiles[y])):
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

                screen.drawImage(sx*res*block.width(), sy*res*block.height(), block)

