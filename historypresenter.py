from PySide.QtCore import Qt
from PySide.QtGui import QGridLayout, QFileDialog

from historydisplay import HistoryDisplay
from historysimulation import HistorySimulation
from planetdata import Data
from simthread import SimThread

class HistoryPresenter(object):
    def __init__(self, view, uistack):
        self._view = view
        self._view.start.clicked.connect(self.start)
        self._view.pause.clicked.connect(self.pause)
        self._view.step.clicked.connect(self.step)
        self._view.load.clicked.connect(self.load)
        self._view.save.clicked.connect(self.save)
        self._view.done.clicked.connect(self.done)

        self._model = HistorySimulation(6)
        self._worker = SimThread(self._model)
        self._worker.tick.connect(self.tick)
        self._worker.simstarted.connect(self.started)
        self._worker.simstopped.connect(self.stopped)
        self._ticks = 0
        self._worker.start()

        self._display = HistoryDisplay(self._model)

        self._view.content.setLayout(QGridLayout())
        self._view.content.layout().addWidget(self._display)

        self._view.rotate.setValue(self._display.rotate)
        self._view.rotate.sliderMoved.connect(self.rotate)

        self._view.aspect.setCurrentIndex(self._display.aspect)
        self._view.aspect.currentIndexChanged[int].connect(self.aspect)

        self._view.rivers.setCheckState(Qt.Checked if self._display.rivers else Qt.Unchecked)
        self._view.rivers.stateChanged.connect(self.rivers)

        self._view.pause.setVisible(False)

        self._uistack = uistack

    def rotate(self, value):
        self._display.rotate = value
        self._view.content.update()

    def aspect(self, value):
        if self._model is None: return
        self._display.aspect = value
        self._display.invalidate()
        self._view.content.update()

    def rivers(self, state):
        self._display.rivers = state == Qt.Checked
        self._display.invalidate()
        self._view.content.update()

    def load(self):
        filename = QFileDialog.getOpenFileName(self._view,
                                               'Load simulation state',
                                               '',
                                               '*{0}'.format(Data.EXTENSION))[0]
        if len(filename) > 0:
            self._model.load(filename)
            self._display.invalidate()
            self._view.content.update()

    def save(self):
        filename = QFileDialog.getSaveFileName(self._view,
                                               'Save simulation state',
                                               '',
                                               '*{0}'.format(Data.EXTENSION))[0]
        if len(filename) > 0:
            self._model.save(filename)

    def done(self):
        self._uistack.pop()

    def started(self):
        self._view.start.setVisible(False)
        self._view.pause.setVisible(True)
        self._view.pause.setEnabled(True)
        self._view.step.setEnabled(False)
        self._view.done.setEnabled(False)

    def stopped(self):
        self._view.start.setVisible(True)
        self._view.start.setEnabled(True)
        self._view.pause.setVisible(False)
        self._view.step.setEnabled(True)
        self._view.done.setEnabled(True)

    def start(self):
        self._view.start.setEnabled(False)
        self._view.step.setEnabled(False)
        self._view.done.setEnabled(False)
        self._worker.simulate(True)

    def pause(self):
        self._view.pause.setEnabled(False)
        self._worker.simulate(False)

    def step(self):
        self._view.start.setEnabled(False)
        self._view.step.setEnabled(False)
        self._model.update()
        self.tick()
        self._view.start.setEnabled(True)
        self._view.step.setEnabled(True)

    def tick(self):
        self._ticks += 1
        self._view.ticks.setNum(self._ticks)
        #self._view.races.setNum(self._model.peoples)
        self._display.invalidate()
        self._view.content.update()
