from PySide.QtGui import QGridLayout, QWidget

import color
from sphereview import SphereView

class HistoryDisplay(QWidget):
    def __init__(self, sim):
        QWidget.__init__(self)
        self._sim = sim
        self._screen = None
        self._rotate = 0
        self.setLayout(QGridLayout())
        self.invalidate()

    @property
    def rotate(self):
        return self._rotate

    @rotate.setter
    def rotate(self, value):
        self._rotate = value
        self._screen.rotate(self._rotate)

    def invalidate(self):
        if self._sim.terrainchanged and self._screen is not None:
            self.layout().removeItem(self.layout().itemAt(0))
            self._screen = None
            self._sim.terrainchanged = False
        if self._screen is None:
            self._screen = SphereView(self._sim.faces, self)
        colors = { }
        for f in self._sim.faces:
            if (f in self._sim.tiles and self._sim.tiles[f].elevation == 0) or not self._sim.faceelevation(f):
                colors[f] = 0, 0, 0
            else:
                p = self._sim.facepopulation(f)
                colors[f] = color.warm(p/17.0) if p else (128, 128, 128)
        self._screen.usecolors(colors)
        self._screen.rotate(self._rotate)
        self.layout().addWidget(self._screen)
