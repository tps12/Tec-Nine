from PySide.QtCore import QThread, Signal

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
                done = self._sim.update()
                self.tick.emit()
                if done:
                  self.simulate(False)
            else:
                if self._stopping:
                    self.simstopped.emit()
                    self._stopping = False
