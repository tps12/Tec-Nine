from PySide.QtGui import QGridLayout, QWidget

import color
from sphereview import SphereView

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

def snoworrock(t):
    return color.snow(t) or color.rock(t) or (0,0,0)

def lifepop(pops, indices, f, i, c):
    pop = sum([(len(pops[t][f][i]) if f in pops[t] else 0) for t in indices])
    return colorscale(pop/(len(indices) * 100.0)) if pop else c

class LifeformsDisplay(QWidget):
    attributeindices = [
        (0,1,2), # life
        (0,), # animals
        (1,), #plants
        (2,)] #trees

    def __init__(self, sim, selecthandler):
        QWidget.__init__(self)
        self._sim = sim
        self._screen = None
        self._rotate = 0
        self.shownattribute = 0
        self.season = 0
        self.glaciation = 0.5
        self._select = selecthandler
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

    def select(self, x, y, z):
        self.selected = self._sim.nearest((z,-x,y)) if abs(z) < 2 else None
        self._select(self.selected)

    def invalidate(self):
        if self._screen is None:
            self._screen = SphereView(self._sim.grid.faces, self)
            self._screen.clicked.connect(self.select)
        pops = self._sim.species()
        indices = self.attributeindices[self.shownattribute]
        fn = lambda v, c: lifepop(pops, indices, v, self.season, c)
        self._screen.usecolors({ v: (255,0,0) if t is self.selected else fn(v, snoworrock(t)) for v, t in self._sim.tiles.iteritems() })
        self._screen.rotate(self._rotate)
        self.layout().addWidget(self._screen)
