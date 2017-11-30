from PySide.QtCore import Qt
from PySide.QtGui import QGridLayout, QFileDialog

from terraindisplay import TerrainDisplay
from terrainsimulation import TerrainSimulation
from planetdata import Data

class TerrainPresenter(object):
    def __init__(self, view, uistack):
        self._view = view
        self._view.load.clicked.connect(self.load)
        self._view.save.clicked.connect(self.save)
        self._view.done.clicked.connect(self.done)

        self._model = TerrainSimulation(6)

        self._display = TerrainDisplay(self._model)

        self._view.content.setLayout(QGridLayout())
        self._view.content.layout().addWidget(self._display)

        self._view.rotate.setValue(self._display.rotate)
        self._view.rotate.sliderMoved.connect(self.rotate)

        self._view.rivers.setCheckState(Qt.Checked if self._display.rivers else Qt.Unchecked)
        self._view.rivers.stateChanged.connect(self.rivers)

        self._uistack = uistack

    def rotate(self, value):
        self._display.rotate = value
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
