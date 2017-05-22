from PySide.QtGui import QApplication, QGridLayout, QFileDialog

from planetdata import Data
from worlddisplay import WorldDisplay
from worldsimulation import WorldSimulation
from simthread import SimThread

class WorldPresenter(object):
    def __init__(self, view, uistack, listitemclass):
        self._view = view
        self._view.start.clicked.connect(self.start)
        self._view.pause.clicked.connect(self.pause)
        self._view.done.clicked.connect(self.done)
        self._view.load.clicked.connect(self.load)
        self._view.save.clicked.connect(self.save)

        self._model = WorldSimulation()
        self._worker = SimThread(self._model)
        self._worker.tick.connect(self.tick)
        self._worker.simstarted.connect(self.started)
        self._worker.simstopped.connect(self.stopped)
        self._worker.start()

        self._display = WorldDisplay(self._model)

        self._view.content.setLayout(QGridLayout())
        self._view.content.layout().addWidget(self._display)

        self._listitemclass = listitemclass

        self._view.rotate.setValue(self._display.rotate)
        self._view.rotate.sliderMoved.connect(self.rotate)

        self._view.aspect.setCurrentIndex(self._display.aspect)
        self._view.aspect.currentIndexChanged[int].connect(self.aspect)

        self._view.pause.setVisible(False)

        self._uistack = uistack

    def selecttile(self, pos):
        self._view.details.clear()
        tile = self._model.sim.tiles[pos[1]][pos[0]] if pos is not None else None
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
        self._view.years.setText(self._model.years)
        self._display.invalidate()
        self._view.content.update()
