from formatpopulation import popstr
from planetdata import Data
from planetsimulation import PlanetSimulation
from prehistorysimulation import PrehistorySimulation

def paleopop(k):
  if k[0] == u'A':
    return 35
  return 5

def agrapop(k):
  if k[0] in u'AC':
    return 150
  if k[0] == u'D':
    return 100
  return 50

class WorldSimulation(object):
  tecdt = 5
  scales = [tecdt * 1000000, PrehistorySimulation.glaciationstep * 250]

  def __init__(self, radius, gridsize, dayhours, tilt, pangeasize, atmdt, lifedt, peopledt):
    spin = 24.0/dayhours
    cells = 7 if spin >= 3 else 5 if spin >= 2 else 3 if spin == 1 else 1
    self._tectonics = PlanetSimulation(radius, gridsize, spin, cells, tilt, pangeasize, self.tecdt, atmdt, lifedt)
    self._prehistory = PrehistorySimulation(gridsize, spin, cells, tilt)
    self._ticks = [0]
    self._stage = 0
    self._peopleticks = peopledt / self.tecdt

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
        return {t: (r, (agrapop if r in self.sim.agricultural else paleopop)(t.climate.koeppen))
                for t, r in self.sim.populated.iteritems()}
    return {}

  @property
  def population(self):
    return popstr(sum([p for (_, p) in self.populated.values()]))

  @property
  def years(self):
    return u'{:,}'.format(sum([self._ticks[i] * self.scales[i] for i in range(len(self._ticks))]))

  def loaddata(self, data):
    self._stage = data['stage']
    self._ticks = [0] * (self._stage+1)
    self._peopleticks = data['peoplet']
    self.sim.loaddata(data)

  def load(self, filename):
    self.loaddata(Data.load(filename))

  def save(self, filename):
    data = self.sim.savedata()
    data['stage'] = self._stage
    data['peoplet'] = self._peopleticks
    Data.save(filename, data)

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
