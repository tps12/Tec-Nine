from PySide.QtGui import QGridLayout, QWidget

import color
from sphereview import SphereView

def population(sim, rivers):
    colors = { }
    for f in sim.faces:
        if (f in sim.tiles and sim.tiles[f].elevation == 0) or not sim.faceelevation(f):
            colors[f] = 0, 0, 0
        elif rivers and any([f in r for r in sim.riverroutes]):
            colors[f] = 0, 0, 255
        else:
            p = sim.facepopulation(f)
            colors[f] = color.warm(p/17.0) if p else (128, 128, 128)
    return colors

def capacity(sim, rivers):
    colors = { }
    for f in sim.faces:
        if (f in sim.tiles and sim.tiles[f].elevation == 0) or not sim.faceelevation(f):
            colors[f] = 0, 0, 0
        elif rivers and any([f in r for r in sim.riverroutes]):
            colors[f] = 0, 0, 255
        else:
            p = sim.facecapacity(f)
            colors[f] = color.warm(p/17.0) if p else (128, 128, 128)
    return colors

class HistoryDisplay(QWidget):
    _colorfunctions = [population, capacity]

    def __init__(self, sim):
        QWidget.__init__(self)
        self._sim = sim
        self._screen = None
        self._rotate = 0
        self._aspect = self._colorfunctions.index(population)
        self._rivers = True
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

    @property
    def rivers(self):
        return self._rivers

    @rivers.setter
    def rivers(self, value):
        if self._rivers != value:
            self._rivers = value
            self.invalidate()

    def tilecolor(self, tile, populated):
        return self._colorfunctions[self._aspect](tile, populated)

    def invalidate(self):
        if self._sim.terrainchanged and self._screen is not None:
            self.layout().removeItem(self.layout().itemAt(0))
            self._screen = None
            self._sim.terrainchanged = False
        if self._screen is None:
            self._screen = SphereView(self._sim.faces, self)
        self._screen.usecolors(self._colorfunctions[self._aspect](self._sim, self._rivers))
        self._screen.rotate(self._rotate)
        self.layout().addWidget(self._screen)
