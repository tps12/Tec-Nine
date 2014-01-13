from PySide.QtGui import QApplication, QGridLayout, QFileDialog

from climatedisplay import ClimateDisplay
from climatesimulation import ClimateSimulation
from planetdata import Data

class ClimatePresenter(object):
    def __init__(self, view, uistack):
        self._view = view
        self._view.earth.clicked.connect(self.earth)
        self._view.load.clicked.connect(self.load)
        self._view.done.clicked.connect(self.done)

        self._model = ClimateSimulation(6400)

        self._display = ClimateDisplay(self._model)

        self._view.earth.setEnabled(self._model.earthavailable)

        self._view.attribute.setCurrentIndex(self._display.shownattribute)
        self._view.attribute.currentIndexChanged[int].connect(self.showattribute)

        self._view.season.sliderMoved.connect(self.season)

        self._view.content.setLayout(QGridLayout())
        self._view.content.layout().addWidget(self._display)

        self._view.rotate.setValue(self._display.rotate)
        self._view.rotate.sliderMoved.connect(self.rotate)

        self._view.cells.setValue(self._model.cells)
        self._view.cells.valueChanged[int].connect(self.cells)

        self._uistack = uistack

    def rotate(self, value):
        self._display.rotate = value
        self._view.content.update()

    def showattribute(self, value):
        self._display.shownattribute = value
        self._view.season.setEnabled(self._display.shownattribute != 0)
        self._display.invalidate()
        self._view.content.update()

    def season(self, value):
        self._display.season = value
        self._display.invalidate()
        self._view.content.update()

    def cells(self, value):
        self._model.cells = value
        self._display.invalidate()
        self._view.content.update()

    def earth(self):
        self._model.earth()
        self._view.season.setValue(0)
        self._view.season.setMaximum(self._model.seasoncount)
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
