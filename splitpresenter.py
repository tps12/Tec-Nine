from random import choice

from PySide.QtGui import QGridLayout, QMenu

from splitpoints import SplitPoints
from splitdisplay import SplitDisplay

class SplitPresenter(object):
    def __init__(self, view, uistack):
        self._view = view
        self._view.reset.clicked.connect(self.reset)
        self._view.done.clicked.connect(self.done)

        self._model = SplitPoints(6400)

        self._display = SplitDisplay(self._model)

        self._view.content.setLayout(QGridLayout())
        self._view.content.layout().addWidget(self._display)

        self._view.rotate.setValue(self._display.rotate)
        self._view.rotate.sliderMoved.connect(self.rotate)

        self._view.time.setValue(self._display.time)
        self._view.time.sliderMoved.connect(self.time)

        self._view.iterate.clicked.connect(self.iterate)
        iterate = QMenu()
        iterate.addAction(self._view.red)
        iterate.addAction(self._view.blue)
        self._view.iterate.setMenu(iterate)

        self._view.red.triggered.connect(self.red)
        self._view.blue.triggered.connect(self.blue)

        self._uistack = uistack

    def iterate(self):
        self._model.iterate(choice([True, False]))
        self._display.invalidate()
        self._view.content.update()

    def red(self):
        self._model.iterate(True)
        self._display.invalidate()
        self._view.content.update()

    def blue(self):
        self._model.iterate(False)
        self._display.invalidate()
        self._view.content.update()

    def rotate(self, value):
        self._display.rotate = value
        self._view.content.update()

    def time(self, value):
        self._display.time = value
        self._view.content.update()

    def done(self):
        self._uistack.pop()

    def reset(self):
        self._model.reset()
        self._display.invalidate()
        self._view.content.update()
