from PySide.QtGui import QGridLayout, QWidget

import color
import koeppencolor
from sphereview import SphereView

def climatecolor(tile):
    h, c = tile.elevation, tile.climate

    if c == None:
        return (127,127,127) if h > 0 else (0,0,0)

    k = c.koeppen

    if h > 0:
        color = koeppencolor.values[k[0]][k[1]]
    else:
        color = 0, 0, 0
    return color

population = color.value

class WorldDisplay(QWidget):
    _colorfunctions = [climatecolor, color.value, population]

    def __init__(self, sim):
        QWidget.__init__(self)
        self._sim = sim
        self._screen = None
        self._rotate = 0
        self._aspect = self._colorfunctions.index(color.value)
        self.selected = None
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
    def aspect(self):
        return self._aspect

    @aspect.setter
    def aspect(self, value):
        self._aspect = value
        self.invalidate()

    def tilecolor(self, tile):
        return self._colorfunctions[self._aspect](tile)

    def invalidate(self):
        if self._screen is None:
            self._screen = SphereView(self._sim.grid, self)
        self._screen.usecolors({ v: self.tilecolor(t) for (v, t) in self._sim.tiles.iteritems() })
        self._screen.rotate(self._rotate)
        self.layout().addWidget(self._screen)
