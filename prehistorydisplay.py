from PySide.QtGui import QGridLayout, QWidget

import color
from sphereview import SphereView

def genshade():
  g = 0
  dg = 255
  while True:
    g += dg
    dg /= -2
    yield (255,g,0)

def genshades(n):
  gen = genshade()
  return [next(gen) for _ in range(n)]

def population(tile, races, shades):
  if tile.elevation <= 0:
    return (0,0,255)
  for i in range(len(races)):
    if tile in races[i]:
      return shades[i]
  return color.value(tile)

class PrehistoryDisplay(QWidget):
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
        shades = genshades(len(self._sim.races))
        self._screen.usecolors({ v: population(t, self._sim.races, shades) for (v, t) in self._sim.tiles.iteritems() })
        self._screen.rotate(self._rotate)
        self.layout().addWidget(self._screen)
