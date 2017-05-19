from PySide.QtGui import QGridLayout, QFileDialog

from riversdisplay import RiversDisplay
from riverssimulation import RiversSimulation
from planetdata import Data
from simthread import SimThread

class RiversPresenter(object):
    def __init__(self, view, uistack):
        self._view = view
        self._view.load.clicked.connect(self.load)
        self._view.done.clicked.connect(self.done)

        self._model = RiversSimulation()

        self._display = RiversDisplay(self._model)

        self._view.content.setLayout(QGridLayout())
        self._view.content.layout().addWidget(self._display)

        self._view.rotate.setValue(self._display.rotate)
        self._view.rotate.sliderMoved.connect(self.rotate)

        self._view.hmin.setValue(self._model.hmin * 10.0)
        self._view.hmin.sliderMoved.connect(self.hmin)

        self._view.pmin.setValue(self._model.pmin/3 * 100.0)
        self._view.pmin.sliderMoved.connect(self.pmin)

        self._uistack = uistack

    def rotate(self, value):
        self._display.rotate = value
        self._view.content.update()

    def hmin(self, value):
        self._model.hmin = value / 10.0
        self._display.invalidate()
        self._view.content.update()

    def pmin(self, value):
        self._model.pmin = 3 * value / 100.0
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

    def done(self):
        self._uistack.pop()
