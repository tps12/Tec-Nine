from random import choice

from PySide.QtCore import Qt
from PySide.QtGui import QGridLayout

from movepoints import MovePoints
from movedisplay import MoveDisplay

class MovePresenter(object):
    def __init__(self, view, uistack):
        self._view = view
        self._view.reset.clicked.connect(self.reset)
        self._view.done.clicked.connect(self.done)

        self._model = MovePoints(6400)

        self._display = MoveDisplay(self._model)

        self._view.content.setLayout(QGridLayout())
        self._view.content.layout().addWidget(self._display)

        self._view.rotate.setValue(self._display.rotate)
        self._view.rotate.sliderMoved.connect(self.rotate)

        self._view.trail.setCheckState(Qt.Checked if self._display.trail else Qt.Unchecked)
        self._view.trail.stateChanged.connect(self.trail)

        self._view.projection.setCurrentIndex(self._display.projection)
        self._view.projection.currentIndexChanged[int].connect(self.project)

        self._view.step.clicked.connect(self.step)

        self._view.direction.sliderMoved.connect(self.direction)
        self._view.speed.sliderMoved.connect(self.speed)
        
        self._model.speed(self._view.speed.value())

        self._view.count.setNum(self._model.count)

        self._uistack = uistack

    def step(self):
        self._model.step()
        self._view.count.setNum(self._model.count)
        self._display.invalidate()
        self._view.content.update()

    def direction(self, value):
        self._model.direction(value)
        self._view.content.update()

    def speed(self, value):
        self._model.speed(value)
        self._view.content.update()

    def rotate(self, value):
        self._display.rotate = value
        self._view.content.update()

    def trail(self, state):
        self._display.trail = state == Qt.Checked
        self._display.invalidate()
        self._view.content.update()

    def project(self, value):
        self._display.projection = value
        self._view.content.update()

    def done(self):
        self._uistack.pop()

    def reset(self):
        self._model.reset(self._view.direction.value(), self._view.speed.value())
        self._display.invalidate()
        self._view.content.update()
