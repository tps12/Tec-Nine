from PySide.QtGui import QGridLayout, QWidget

import color
from sphereview import SphereView

nationcolors = [(165, 125, 175), # lavender
                (125, 175, 125), # green
                (125, 175, 175), # blue
                (165, 175, 125), # yellow
                (175, 125, 125), # pink
                (175, 135, 125)] # orange

def phase(sim, f):
    if sim.phase == 'species':
        count = sim.facespeciescount(f)/2000
        if count > 0:
            return color.warm(count)
    elif sim.phase in ('nations', 'coasts'):
        n = facenationcolor(sim, f)
        if n is not None:
            return nationcolors[n]
    elif sim.phase == 'langs':
        count = sim.facewordcount(f)/2000
        if count > 0:
            return color.cool(count)
    return (128, 128, 128)

def selectednationcolor(sim, f, selectednations):
    if f in sim.boundaries:
        n = sim.boundaries[f]
        if n == selectednations[0]:
            return (0, 255, 0)
        if n in selectednations[1]:
            return (255, 255, 0)
        if n in selectednations[2]:
            return (255, 0, 0)
    return None

def facenationcolor(sim, f):
    if f in sim.boundaries:
        n = sim.boundaries[f]
        if n < len(sim.nationcolors):
            return sim.nationcolors[n]
    return None

def nations(sim, rivers, selectednations):
    colors = { }
    for f in sim.faces:
        if (f in sim.tiles and sim.tiles[f].elevation == 0) or not sim.faceelevation(f):
            colors[f] = 0, 0, 255
            continue
        if rivers and any([f in r for r in sim.riverroutes]):
            colors[f] = 0, 0, 255
            continue
        if sim.phase != 'sim':
            colors[f] = phase(sim, f)
            continue
        s = selectednationcolor(sim, f, selectednations)
        if s is not None:
            colors[f] = s
            continue
        t = sim.facehighlighted(f)
        if t is not None:
            colors[f] = (0, 128, 0) if t == 'trade' else (128, 0, 0)
            continue
        n = facenationcolor(sim, f)
        if n is not None:
            colors[f] = nationcolors[n]
        else:
            p = sim.facepopulation(f)
            colors[f] = color.warm(p/17.0) if p else (128, 128, 128)
    return colors

def species(sim, rivers, _):
    colors = { }
    for f in sim.faces:
        if (f in sim.tiles and sim.tiles[f].elevation == 0) or not sim.faceelevation(f):
            colors[f] = 0, 0, 255
        elif rivers and any([f in r for r in sim.riverroutes]):
            colors[f] = 0, 0, 255
        elif sim.phase != 'sim':
            colors[f] = phase(sim, f)
        else:
            s = sim.facenationspecies(f)
            colors[f] = color.warm(len(s)/2000) if s else (128, 128, 128)
    return colors

def population(sim, rivers, _):
    colors = { }
    for f in sim.faces:
        if (f in sim.tiles and sim.tiles[f].elevation == 0) or not sim.faceelevation(f):
            colors[f] = 0, 0, 255
        elif rivers and any([f in r for r in sim.riverroutes]):
            colors[f] = 0, 0, 255
        elif sim.phase != 'sim':
            colors[f] = phase(sim, f)
        else:
            p = sim.facepopulation(f)
            colors[f] = color.warm(p/17.0) if p else (128, 128, 128)
    return colors

def capacity(sim, rivers, _):
    colors = { }
    for f in sim.faces:
        if (f in sim.tiles and sim.tiles[f].elevation == 0) or not sim.faceelevation(f):
            colors[f] = 0, 0, 255
        elif rivers and any([f in r for r in sim.riverroutes]):
            colors[f] = 0, 0, 255
        elif sim.phase != 'sim':
            colors[f] = phase(sim, f)
        else:
            p = sim.facecapacity(f)
            colors[f] = color.warm(p/17.0) if p else (128, 128, 128)
    return colors

class HistoryDisplay(QWidget):
    _colorfunctions = [nations, species, population, capacity]

    def __init__(self, sim, selecthandler):
        QWidget.__init__(self)
        self._sim = sim
        self._screen = None
        self._rotate = 0
        self._aspect = self._colorfunctions.index(nations)
        self._rivers = True
        self._select = selecthandler
        self._selectednations = (None, set(), set())
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
    def aspect(self):
        return self._aspect

    @aspect.setter
    def aspect(self, value):
        self._aspect = value
        self.invalidate()

    @property
    def rivers(self):
        return self._rivers

    @rivers.setter
    def rivers(self, value):
        if self._rivers != value:
            self._rivers = value
            self.invalidate()

    def tilecolor(self, tile, populated):
        return self._colorfunctions[self._aspect](tile, populated)

    def select(self, x, y, z):
        self._select(self._sim.nearest((z,-x,y)) if abs(z) < 2 else None)

    def selectnations(self, n, ps, cs):
        self._selectednations = (n, ps, cs)

    def invalidate(self):
        if self._sim.terrainchanged and self._screen is not None:
            self.layout().removeItem(self.layout().itemAt(0))
            self._screen = None
            self._sim.terrainchanged = False
        if self._screen is None:
            self._screen = SphereView(self._sim.faces, self)
            self._screen.clicked.connect(self.select)
        self._screen.usecolors(self._colorfunctions[self._aspect](self._sim, self._rivers, self._selectednations))
        self._screen.rotate(self._rotate)
        self.layout().addWidget(self._screen)
