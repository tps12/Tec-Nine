from PySide6.QtWidgets import QGridLayout, QFileDialog

from populationdisplay import PopulationDisplay
from populationsimulation import PopulationSimulation
from planetdata import Data
from simthread import SimThread

class PopulationPresenter(object):
    def __init__(self, view, uistack):
        self._view = view
        self._view.start.clicked.connect(self.start)
        self._view.pause.clicked.connect(self.pause)
        self._view.load.clicked.connect(self.load)
        self._view.done.clicked.connect(self.done)

        self._model = PopulationSimulation()
        self._worker = SimThread(self._model)
        self._worker.tick.connect(self.tick)
        self._worker.simstarted.connect(self.started)
        self._worker.simstopped.connect(self.stopped)
        self._ticks = 0
        self._worker.start()

        self._display = PopulationDisplay(self._model)

        self._view.content.setLayout(QGridLayout())
        self._view.content.layout().addWidget(self._display)

        self._view.rotate.setValue(self._display.rotate)
        self._view.rotate.sliderMoved.connect(self.rotate)

        self._view.pause.setVisible(False)

        self._view.coastprox.setValue(self._model.coastprox)
        self._view.coastprox.valueChanged[int].connect(self.coastprox)

        self._view.range.setValue(self._model.range)
        self._view.range.valueChanged[int].connect(self.range)

        self._uistack = uistack

    def rotate(self, value):
        self._display.rotate = value
        self._view.content.update()

    def coastprox(self, value):
        self._model.coastprox = value

    def range(self, value):
        self._model.range = value

    def load(self):
        filename = QFileDialog.getOpenFileName(self._view,
                                               'Load simulation state',
                                               '',
                                               '*{0}'.format(Data.EXTENSION))[0]
        if len(filename) > 0:
            self._model.load(filename)
            self._display.invalidate()
            self._view.content.update()

    def done(self):
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
        self._display.invalidate()
        self._view.content.update()
