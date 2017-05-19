from PySide.QtGui import QGridLayout, QWidget

import color
from sphereview import SphereView

def highlightriver(t, rts):
  if t in rts:
    return (127,255,255)
  return color.value(t)

class RiversDisplay(QWidget):
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
        if self._screen is None:
            self._screen = SphereView(self._sim.grid, self)
        rts = set()
        for t in self._sim.tiles.itervalues():
            for r in self._sim.rivers:
                if t in r:
                    rts.add(t)
        self._screen.usecolors({ v: highlightriver(t, rts) for (v, t) in self._sim.tiles.iteritems() })
        self._screen.rotate(self._rotate)
        self.layout().addWidget(self._screen)
