from PySide.QtGui import QApplication, QGridLayout, QFileDialog

from lifeformsdisplay import LifeformsDisplay
from lifeformssimulation import LifeformsSimulation
from planetdata import Data

class LifeformsPresenter(object):
    def __init__(self, view, uistack, detailsitemclass):
        self._view = view
        self._view.load.clicked.connect(self.load)
        self._view.done.clicked.connect(self.done)

        self._model = LifeformsSimulation(6)

        self._display = LifeformsDisplay(self._model, self.selecttile)

        self._view.attribute.setCurrentIndex(self._display.shownattribute)
        self._view.attribute.currentIndexChanged[int].connect(self.showattribute)

        self._view.season.sliderMoved.connect(self.season)

        self._view.glaciation.valueChanged.connect(self.glaciation)

        self._view.content.setLayout(QGridLayout())
        self._view.content.layout().addWidget(self._display)

        self._view.rotate.setValue(self._display.rotate)
        self._view.rotate.sliderMoved.connect(self.rotate)

        self._detailsitemclass = detailsitemclass

        self._uistack = uistack

    def selecttile(self, tile):
        self._display.invalidate()
        self._view.content.update()
        self._view.details.clear()
        if tile is not None:
            for f, t in self._model.tiles.iteritems():
                if t is tile:
                    species = []
                    for i in LifeformsDisplay.attributeindices[self._display.shownattribute]:
                        t = self._model.species()[i]
                        if f not in t:
                            continue
                        pop = t[f]
                        species += [s.name for s in pop[self._display.season]]
                    for s in sorted(species):
                        self._view.details.addItem(self._detailsitemclass(s))
                    break

    def rotate(self, value):
        self._display.rotate = value
        self._display.invalidate()
        self._view.content.update()

    def showattribute(self, value):
        self._display.shownattribute = value
        self._display.invalidate()
        self._view.content.update()
        self.selecttile(self._display.selected)

    def season(self, value):
        self._display.season = int(round((len(self._model.seasons)-1) * value/100.0))
        self._display.invalidate()
        self._view.content.update()
        self.selecttile(self._display.selected)

    def glaciation(self, _):
        glaciation = 1 - self._view.glaciation.sliderPosition()/100.0
        if self._model.glaciation == glaciation:
            return
        self._model.glaciation = glaciation
        self._display.invalidate()
        self._view.content.update()
        self.selecttile(self._display.selected)

    def load(self):
        filename = QFileDialog.getOpenFileName(self._view,
                                               'Load simulation state',
                                               '',
                                               '*{0}'.format(Data.EXTENSION))[0]
        if len(filename) > 0:
            self._model.load(filename)
            self._display.invalidate()
            self._view.content.update()
            self.selecttile(self._display.selected)

    def done(self):
        self._uistack.pop()
