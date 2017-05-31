import random

from planetdata import Data
from planetsimulation import PlanetSimulation
from prehistorysimulation import PrehistorySimulation

class WorldSimulation(object):
  tecdt = 5
  scales = [tecdt * 1000000, PrehistorySimulation.glaciationstep * 250]

  def __init__(self):
    self._tectonics = PlanetSimulation(6400, self.tecdt)
    self._prehistory = PrehistorySimulation()
    self._ticks = [0]
    self._stage = 0

  @property
  def sim(self):
    if self._stage == 0:
      return self._tectonics
    elif self._stage == 1:
      return self._prehistory

  @property
  def grid(self):
    return self.sim.grid

  @property
  def tiles(self):
    return self.sim.tiles

  @property
  def populated(self):
    if 'populated' in self.sim.__dict__:
        return {t: 35 if t.climate.koeppen[0] == u'A' else 5
                for t in self.sim.populated}
    return {}

  @property
  def population(self):
    return u'{:,}'.format(sum(self.populated.values()) * 1000)

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
    if self._stage == 0 and self.sim.haslife and random.random() < 0.05:
      data = self.sim.savedata()
      self._stage += 1
      self._ticks += [0]
      self.sim.loaddata(Data.loaddata(data))
