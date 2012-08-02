from random import choice

from PySide.QtCore import Qt
from PySide.QtGui import QGridLayout

from fillholes import FillHoles
from holesdisplay import HolesDisplay

class HolesPresenter(object):
    def __init__(self, view, uistack):
        self._view = view
        self._view.reset.clicked.connect(self.reset)
        self._view.done.clicked.connect(self.done)

        self._view.domove.setChecked(Qt.Unchecked)
        self._view.random.setChecked(Qt.Checked)
        for makeholes in self._view.domove, self._view.random:
            makeholes.toggled.connect(self.makeholes)

        for holesize in self._view.small, self._view.large:
            holesize.setCheckState(Qt.Checked)
            holesize.setEnabled(True)

        self._model = FillHoles(6400)
        self._view.time.setNum(self._model.time)

        self._display = HolesDisplay(self._model)

        self._view.content.setLayout(QGridLayout())
        self._view.content.layout().addWidget(self._display)

        self._view.rotate.setValue(self._display.rotate)
        self._view.rotate.sliderMoved.connect(self.rotate)

        self._view.showholes.setCheckState(Qt.Checked if self._display.show else Qt.Unchecked)
        self._view.showholes.stateChanged.connect(self.show)

        self._view.projection.setCurrentIndex(self._display.projection)
        self._view.projection.currentIndexChanged[int].connect(self.project)
       
        self._view.count.setNum(self._model.count)

        self._uistack = uistack

    def rotate(self, value):
        self._display.rotate = value
        self._view.content.update()

    def show(self, state):
        self._display.show = state == Qt.Checked
        self._display.invalidate()
        self._view.content.update()

    def project(self, value):
        self._display.projection = value
        self._view.content.update()

    def done(self):
        self._uistack.pop()

    def reset(self):
        self._model.reset(self._view.domove.isChecked(),
                          self._view.random.isChecked() and self._view.small.isChecked(),
                          self._view.random.isChecked() and self._view.large.isChecked())
        self._view.time.setNum(self._model.time)
        self._display.invalidate()
        self._view.content.update()

    def makeholes(self, state):
        sizeenabled = self._view.random.isChecked()
        for holesize in self._view.small, self._view.large:
            holesize.setEnabled(sizeenabled)
