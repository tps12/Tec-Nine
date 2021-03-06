import math
import random

from PySide.QtCore import Qt
from PySide.QtGui import QApplication, QGridLayout, QFileDialog

from formatpopulation import popstr
from planetdata import Data
from worlddisplay import WorldDisplay
from worldsimulation import WorldSimulation
from simthread import SimThread

climatenames = {
    u'BW': 'desert',
    u'BS': 'steppe',
    u'Af': 'rainforest',
    u'Am': 'monsoon',
    u'Aw': 'savanna',
    u'Cf': 'temperate',
    u'Cs': 'temperate, dry summer',
    u'Cw': 'temperate, dry winter',
    u'Df': 'cold',
    u'Ds': 'cold, dry summer',
    u'Dw': 'cold, dry winter',
    u'ET': 'tundra',
    u'EF': 'ice cap' }

# Return a random value from the given spin box, favoring m (twice as likely to
# return m as either the min or max, with probability sloping on either side).
def randomspinvalue(b, m):
    r = range(b.minimum(), b.maximum() + b.singleStep(), b.singleStep())
    pw = 0
    ws = []
    for v in r:
        dw = float(v - r[0])/(m - r[0]) if v < m else float(r[-1] - v)/(r[-1] - m)
        w = pw + (1 + dw)
        ws.append(w)
        pw = w
    f = random.uniform(0, pw)
    for i in range(len(r)):
        if f < ws[i]:
            return r[i]

def randomticks():
    n = 0
    while True:
        if random.random() < 0.05:
            return n
        n += 1

def randomtime():
    return WorldSimulation.tecdt * (1 + randomticks())

class WorldPresenter(object):
    radii_and_grid_sizes = [
        (2100, 4),
        (3700, 5),
        (6400, 6),
        (11000, 7),
        (19000, 8)]
    day_hours = [8, 12, 24, 48]

    def __init__(self, view, uistack, listitemclass):
        self._view = view
        self._view.randomize.stateChanged.connect(self.randomized)
        self._view.create.clicked.connect(self.create)
        self._view.start.clicked.connect(self.start)
        self._view.pause.clicked.connect(self.pause)
        self._view.done.clicked.connect(self.done)
        self._view.load.clicked.connect(self.load)
        self._view.save.clicked.connect(self.save)

        self._listitemclass = listitemclass

        self._uistack = uistack

        self._model = None
        self._view.randomize.setCheckState(Qt.Checked)
        self._view.start.setVisible(True)
        self._view.start.setEnabled(False)
        self._view.pause.setVisible(False)
        self._view.done.setEnabled(True)

    def randomized(self, value):
        randomize = value == Qt.Checked
        for param in [self._view.spin, self._view.tilt, self._view.land, self._view.atmt, self._view.lifet, self._view.peoplet]:
            param.setEnabled(not randomize)

    def create(self, gridsize=None):
        if self._model is not None:
            self._worker.stop()
            self._worker.wait()
            layout = self._view.content.layout()
            if layout.count():
                layout.removeItem(layout.itemAt(0))

        if self._view.randomize.checkState() == Qt.Checked:
            # Randomize values, but favor Earth-like ones.
            self._view.spin.setCurrentIndex(random.choice([0,1,1,2,2,2,3,3]))
            self._view.tilt.setValue(randomspinvalue(self._view.tilt, 23))
            self._view.land.setValue(randomspinvalue(self._view.land, 29))
            self._view.atmt.setValue(randomtime())
            self._view.lifet.setValue(randomtime())
            self._view.peoplet.setValue(randomtime())

        r, g = self.radii_and_grid_sizes[self._view.radius.currentIndex()]
        land_r = math.sqrt(0.04 * self._view.land.value())
        self._model = WorldSimulation(r, gridsize or g, self.day_hours[self._view.spin.currentIndex()], self._view.tilt.value(), land_r, self._view.atmt.value(), self._view.lifet.value(), self._view.peoplet.value())
        self._worker = SimThread(self._model)
        self._worker.tick.connect(self.tick)
        self._worker.simstarted.connect(self.started)
        self._worker.simstopped.connect(self.stopped)
        self._worker.start()

        self._display = WorldDisplay(self._model, self.selecttile)

        self._view.content.setLayout(QGridLayout())
        self._view.content.layout().addWidget(self._display)

        self._view.rotate.setValue(self._display.rotate)
        self._view.rotate.sliderMoved.connect(self.rotate)

        self._view.aspect.setCurrentIndex(self._display.aspect)
        self._view.aspect.currentIndexChanged[int].connect(self.aspect)

        self._view.start.setVisible(True)
        self._view.start.setEnabled(True)
        self._view.pause.setVisible(False)
        self._view.done.setEnabled(True)

    def selecttile(self, tile):
        self._display.invalidate()
        self._view.content.update()
        self._view.details.clear()
        if tile is not None:
            rock = self._listitemclass(['Layers'])
            for layer in reversed(tile.layers):
                name = self._listitemclass([layer.rock['name']])
                name.setToolTip(0, repr({ 'thickness': layer.thickness,
                                          'rock': layer.rock }))
                rock.addChild(name)
            self._view.details.addTopLevelItem(rock)
            if tile.elevation > 0 and tile.climate:
                climate = self._listitemclass([climatenames[tile.climate.koeppen]])
                climate.setToolTip(0, repr({ 'temperature': tile.climate.temperature,
                                             'precipitation': tile.climate.precipitation }))
                self._view.details.addTopLevelItem(climate)
            populated = self._model.populated
            if tile in populated:
                heritage, count = populated[tile]
                population = self._listitemclass([popstr(count)])
                def ancestors(h, p):
                    item = self._listitemclass([h.name])
                    for a in h.ancestry or []:
                        ancestors(a, item)
                    p.addChild(item)
                ancestors(heritage, population)
                self._view.details.addTopLevelItem(population)

    def rotate(self, value):
        if self._model is None: return
        self._display.rotate = value
        self._view.content.update()

    def aspect(self, value):
        if self._model is None: return
        self._display.aspect = value
        self._display.invalidate()
        self._view.content.update()

    def load(self):
        filename = QFileDialog.getOpenFileName(self._view,
                                               'Load simulation state',
                                               '',
                                               '*{0}'.format(Data.EXTENSION))[0]
        if len(filename) > 0:
            data = Data.load(filename)
            self.create(data['gridsize'])
            self._model.loaddata(data)
            self._view.content.update()
            self.tick()

    def save(self):
        if self._model is None: return
        filename = QFileDialog.getSaveFileName(self._view,
                                               'Save simulation state',
                                               '',
                                               '*{0}'.format(Data.EXTENSION))[0]
        if len(filename) > 0:
            self._model.save(filename)

    def done(self):
        if self._model is not None:
            self._worker.stop()
            self._worker.wait()
        self._uistack.pop()

    def started(self):
        self._view.start.setVisible(False)
        self._view.pause.setVisible(True)
        self._view.pause.setEnabled(True)
        self._view.done.setEnabled(False)

    def stopped(self):
        self._view.start.setVisible(True)
        self._view.start.setEnabled(True)
        self._view.pause.setVisible(False)
        self._view.done.setEnabled(True)

    def start(self):
        if self._model is None: return
        self._view.start.setEnabled(False)
        self._view.done.setEnabled(False)
        self._worker.simulate(True)

    def pause(self):
        if self._model is None: return
        self._view.pause.setEnabled(False)
        self._worker.simulate(False)

    def tick(self):
        self._view.years.setText(self._model.years)
        self._view.population.setText(self._model.population)
        self._display.invalidate()
        self._view.content.update()
