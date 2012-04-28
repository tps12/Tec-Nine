from time import sleep

from PySide.QtGui import QApplication, QGridLayout
from PySide.QtCore import QThread, Signal

from planetdisplay import PlanetDisplay
from planetsimulation import PlanetSimulation

class SimThread(QThread):
    tick = Signal()
    simstarted = Signal()
    simstopped = Signal()

    def __init__(self, sim):
        QThread.__init__(self)
        self._sim = sim
        self._running = self._starting = self._stopping = False
        self._stop = False

    def simulate(self, running):
        if self._running == running:
            return

        self._running = running
        if running:
            self._starting = True
        else:
            self._stopping = True

    def stop(self):
        self._stop = True

    def run(self):
        while not self._stop:
            if self._running:
                if self._starting:
                    self.simstarted.emit()
                    self._starting = False
                self._sim.update()
                self.tick.emit()
            else:
                if self._stopping:
                    self.simstopped.emit()
                    self._stopping = False
                sleep(0.1)

class TectonicsPresenter(object):
    def __init__(self, view, uistack):
        self._view = view
        self._view.start.clicked.connect(self.start)
        self._view.pause.clicked.connect(self.pause)
        self._view.done.clicked.connect(self.done)

        self._model = PlanetSimulation(6400, 5)
        self._worker = SimThread(self._model)
        self._worker.tick.connect(self.tick)
        self._worker.simstarted.connect(self.started)
        self._worker.simstopped.connect(self.stopped)
        self._ticks = 0
        self._worker.start()

        self._display = PlanetDisplay(self._model)

        self._view.content.setLayout(QGridLayout())
        self._view.content.layout().addWidget(self._display)

        self._view.rotate.setValue(self._display.rotate)
        self._view.rotate.sliderMoved.connect(self.rotate)

        self._view.pause.setVisible(False)

        self._uistack = uistack

    def rotate(self, value):
        self._display.rotate = value
        self._view.content.update()

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
        self._view.content.update()