from PySide.QtGui import QApplication, QGridLayout, QFileDialog

from planetdata import Data
from planetdisplay import PlanetDisplay
from planetsimulation import PlanetSimulation
from simthread import SimThread

class TectonicsPresenter(object):
    def __init__(self, view, uistack, listitemclass):
        self._view = view
        self._view.start.clicked.connect(self.start)
        self._view.pause.clicked.connect(self.pause)
        self._view.done.clicked.connect(self.done)
        self._view.load.clicked.connect(self.load)
        self._view.save.clicked.connect(self.save)

        self._model = PlanetSimulation(6400, 6, 1.0, 3, 23, 1.145, 5, 125, 125)
        self._worker = SimThread(self._model)
        self._worker.tick.connect(self.tick)
        self._worker.simstarted.connect(self.started)
        self._worker.simstopped.connect(self.stopped)
        self._ticks = 0
        self._worker.start()

        self._display = PlanetDisplay(self._model, self.selecttile)

        self._view.continents.setNum(self._model.continents)
        self._view.percent.setNum(self._model.land)

        self._view.content.setLayout(QGridLayout())
        self._view.content.layout().addWidget(self._display)

        self._listitemclass = listitemclass

        self._view.rotate.setValue(self._display.rotate)
        self._view.rotate.sliderMoved.connect(self.rotate)

        self._view.aspect.setCurrentIndex(self._display.aspect)
        self._view.aspect.currentIndexChanged[int].connect(self.aspect)

        self._view.pause.setVisible(False)

        self._uistack = uistack

    def selecttile(self, tile):
        self._view.details.clear()
        if tile is not None:
            for layer in reversed(tile.layers):
                name = self._listitemclass(layer.rock['name'])
                name.setToolTip(repr({ 'thickness': layer.thickness,
                                       'rock': layer.rock }))
                self._view.details.addItem(name)

    def rotate(self, value):
        self._display.rotate = value
        self._view.content.update()

    def aspect(self, value):
        self._display.aspect = value
        self._display.invalidate()
        self._view.content.update()

    def load(self):
        filename = QFileDialog.getOpenFileName(self._view,
                                               'Load simulation state',
                                               '',
                                               '*{0}'.format(Data.EXTENSION))[0]
        if len(filename) > 0:
            self._model.load(filename)
            self._view.content.update()
            self._ticks = -1
            self.tick()

    def save(self):
        filename = QFileDialog.getSaveFileName(self._view,
                                               'Save simulation state',
                                               '',
                                               '*{0}'.format(Data.EXTENSION))[0]
        if len(filename) > 0:
            self._model.save(filename)

    def done(self):
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
        self._view.start.setEnabled(False)
        self._view.done.setEnabled(False)
        self._worker.simulate(True)

    def pause(self):
        self._view.pause.setEnabled(False)
        self._worker.simulate(False)

    def tick(self):
        self._ticks += 1
        self._view.ticks.setNum(self._ticks)
        self._view.continents.setNum(self._model.continents)
        self._view.percent.setNum(self._model.land)
        self._display.invalidate()
        self._view.content.update()
