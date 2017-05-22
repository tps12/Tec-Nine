import random

from planetdata import Data
from planetsimulation import PlanetSimulation

class WorldSimulation(object):
  tecdt = 5
  scales = [tecdt * 1000000, 2000]

  def __init__(self):
    self._tectonics = PlanetSimulation(6400, self.tecdt)
    self._ticks = [0]
    self._stage = 0

  @property
  def sim(self):
    if self._stage == 0:
      return self._tectonics

  @property
  def grid(self):
    return self.sim.grid

  @property
  def tiles(self):
    return self.sim.tiles

  @property
  def years(self):
    return u'{:,}'.format(sum([self._ticks[i] * self.scales[i] for i in range(len(self._ticks))]))

  def load(self, filename):
    data = Data.load(filename)
    self._stage = data['stage']
    self._ticks = [0] * (self._stage+1)
    self.sim.loaddata(data)

  def save(self, filename):
    data = self.sim.savedata()
    data['stage'] = self._stage
    Data.save(filename, data)

  def update(self):
    self.sim.update()
    self._ticks[self._stage] += 1
