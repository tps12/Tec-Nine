from PySide.QtGui import QGridLayout, QWidget

import color
from sphereview import SphereView

def interpolate(f, ts):
    if not hasattr(ts, '__iter__'):
        return f(ts)
    vs = [interpolate(f, t) for t in ts]
    n = len(vs)
    return tuple([sum([v[i] for v in vs])/n for i in range(3)])

class TerrainDisplay(QWidget):
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
        if self._screen is not None:
            self.layout().removeItem(self.layout().itemAt(0))
        self._screen = SphereView(self._sim.faces, self)
        colors = { v: color.elevation(t) for (v, t) in self._sim.tiles.iteritems() }
        for v in self._sim.faces:
            if v not in colors:
                colors[v] = interpolate(color.elevation, self._sim.facecomponents(v))
        self._screen.usecolors(colors)
        self._screen.rotate(self._rotate)
        self.layout().addWidget(self._screen)
