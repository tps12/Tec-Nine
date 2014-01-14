from PySide.QtCore import Qt
from PySide.QtGui import QApplication, QGridLayout, QFileDialog

from erosiondisplay import ErosionDisplay
from erosionsimulation import ErosionSimulation
from planetdata import Data

class ErosionPresenter(object):
    def __init__(self, view, uistack):
        self._view = view
        self._view.earth.clicked.connect(self.earth)
        self._view.load.clicked.connect(self.load)
        self._view.done.clicked.connect(self.done)

        self._model = ErosionSimulation(6400)

        self._display = ErosionDisplay(self._model)

        self._view.earth.setEnabled(self._model.earthavailable)

        self._view.content.setLayout(QGridLayout())
        self._view.content.layout().addWidget(self._display)

        self._view.lost.setCheckState(Qt.Checked if self._display.lost else Qt.Unchecked)
        self._view.lost.stateChanged.connect(self.lost)

        self._view.gained.setCheckState(Qt.Checked if self._display.gained else Qt.Unchecked)
        self._view.gained.stateChanged.connect(self.gained)

        self._view.rotate.setValue(self._display.rotate)
        self._view.rotate.sliderMoved.connect(self.rotate)

        self._view.projection.setCurrentIndex(self._display.projection)
        self._view.projection.currentIndexChanged[int].connect(self.project)

        self._uistack = uistack

    def lost(self, state):
        self._display.lost = state == Qt.Checked
        self._display.invalidate()
        self._view.content.update()

    def gained(self, state):
        self._display.gained = state == Qt.Checked
        self._display.invalidate()
        self._view.content.update()

    def rotate(self, value):
        self._display.rotate = value
        self._view.content.update()

    def project(self, value):
        self._display.projection = value
        self._view.content.update()

    def earth(self):
        self._model.earth()
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
