from math import sin, cos, pi

from PySide.QtGui import QColor, QGridLayout, QImage, QPainter, QWidget, QSizePolicy

import color
from sphereview import SphereView

def highlightcoast(tile, populated):
  if tile.climate is None:
    return (127,127,127)
  if tile in populated:
    return (255,255,0)
  return color.value(tile)

class PopulationDisplay(QWidget):
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
            self._screen = SphereView(self._sim.grid.faces, self)
        self._screen.usecolors({ v: highlightcoast(t, self._sim.populated) for (v, t) in self._sim.tiles.items() })
        self._screen.rotate(self._rotate)
        self.layout().addWidget(self._screen)
