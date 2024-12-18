from formatpopulation import popstr
from planetdata import Data
from planetsimulation import PlanetSimulation
import populationlevel
from prehistorysimulation import PrehistorySimulation

class WorldSimulation(object):
  tecdt = 5
  scales = [tecdt * 1000000, PrehistorySimulation.glaciationstep * 250]

  def __init__(self):
    self._tectonics = PlanetSimulation()
    self._prehistory = PrehistorySimulation()

  def create(self, radius, gridsize, dayhours, tilt, pangeasize, atmdt, lifedt, peopledt):
    spin = 24.0/dayhours
    cells = 7 if spin >= 3 else 5 if spin >= 2 else 3 if spin == 1 else 1
    self._tectonics.create(radius, gridsize, spin, cells, tilt, pangeasize, self.tecdt, atmdt, lifedt)
    self._prehistory.create(gridsize, spin, cells, tilt)
    self._ticks = [0]
    self._stage = 0
    self._peopleticks = peopledt / self.tecdt
    return self

  def nearest(self, loc):
    return self.sim.nearest(loc)

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
        return {t: (r, populationlevel.count(t, r, self.sim.agricultural))
                for t, r in self.sim.populated.items()}
    return {}

  @property
  def population(self):
    return popstr(sum([p for (_, p) in self.populated.values()]))

  @property
  def years(self):
    return u'{:,}'.format(sum([self._ticks[i] * self.scales[i] for i in range(len(self._ticks))]))

  def loaddata(self, data):
    self._stage = data['stage']
    self._ticks = data.get('ticks', [0] * (self._stage+1))
    self._peopleticks = data['peoplet']
    self.sim.loaddata(data)

  def load(self, filename):
    self.loaddata(Data.load(filename))

  def savedata(self):
    data = self.sim.savedata()
    data['stage'] = self._stage
    data['ticks'] = self._ticks
    data['peoplet'] = self._peopleticks
    return data

  def save(self, filename):
    Data.save(filename, self.savedata())

  def update(self):
    self.sim.update()
    self._ticks[self._stage] += 1
    if self._stage == 0 and self.sim.haslife:
      if self._peopleticks == 0:
        data = self.sim.savedata()
        self._stage += 1
        self._ticks += [0]
        self.sim.loaddata(Data.loaddata(data))
      else:
        self._peopleticks -= 1
