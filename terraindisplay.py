from PySide.QtGui import QGridLayout, QWidget

import color
from sphereview import SphereView

class TerrainDisplay(QWidget):
    def __init__(self, sim):
        QWidget.__init__(self)
        self._sim = sim
        self._screen = None
        self._rotate = 0
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
    def rivers(self):
        return self._rivers

    @rivers.setter
    def rivers(self, value):
        if self._rivers != value:
            self._rivers = value
            self.invalidate()

    def isriver(self, v):
        return self._rivers and any([v in r for r in self._sim.riverroutes])

    def invalidate(self):
        if self._sim.terrainchanged and self._screen is not None:
            self.layout().removeItem(self.layout().itemAt(0))
            self._screen = None
            self._sim.terrainchanged = False
        if self._screen is None:
            self._screen = SphereView(self._sim.faces, self)
        colors = { v: (0,0,255) if self.isriver(v) else color.elevationcolor(self._sim.faceelevation(v)) for v in self._sim.faces }
        self._screen.usecolors(colors)
        self._screen.rotate(self._rotate)
        self.layout().addWidget(self._screen)
