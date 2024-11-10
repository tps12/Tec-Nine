from PySide6.QtWidgets import QGridLayout

from racinationdisplay import RacinationDisplay
from racinationsimulation import RacinationSimulation

class RacinationPresenter(object):
    def __init__(self, view, uistack):
        self._view = view
        self._view.reset.clicked.connect(self.reset)
        self._view.isolate.clicked.connect(self.isolate)
        self._view.done.clicked.connect(self.done)

        self._model = RacinationSimulation()
        self._display = RacinationDisplay(self._model)

        self._view.content.setLayout(QGridLayout())
        self._view.content.layout().addWidget(self._display)

        self._view.rotate.setValue(self._display.rotate)
        self._view.rotate.sliderMoved.connect(self.rotate)

        self._view.range.setValue(self._model.range)
        self._view.range.valueChanged[int].connect(self.range)

        self._view.races.setNum(self._model.peoples)

        self._uistack = uistack

    def rotate(self, value):
        self._display.rotate = value
        self._view.content.update()

    def reset(self):
        self._model.reset()
        self._view.races.setNum(self._model.peoples)
        self._display.invalidate()
        self._view.content.update()

    def range(self, value):
        self._model.range = value

    def isolate(self):
        self._model.isolate()
        self._view.races.setNum(self._model.peoples)
        self._display.invalidate()
        self._view.content.update()

    def done(self):
        self._uistack.pop()
