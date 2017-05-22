from climate import Climate
from erosion import Erosion
from options import Options
from population import Population
from prehistory import Prehistory
from racination import Racination
from rivers import Rivers
from tectonics import Tectonics
from split import Split
from world import World
from move import Move

class MainMenuPresenter(object):
    def __init__(self, view, uistack):
        self._view = view
        self._view.start.clicked.connect(self.start)
        self._view.tectonics.clicked.connect(self.tectonics)
        self._view.climate.clicked.connect(self.climate)
        self._view.rivers.clicked.connect(self.rivers)
        self._view.erosion.clicked.connect(self.erosion)
        self._view.population.clicked.connect(self.population)
        self._view.racination.clicked.connect(self.racination)
        self._view.prehistory.clicked.connect(self.prehistory)
        self._view.split.clicked.connect(self.split)
        self._view.movepoints.clicked.connect(self.move)
        self._view.options.clicked.connect(self.options)
        self._view.exit.clicked.connect(self.exit)
        self._uistack = uistack

    def exit(self):
        self._uistack.pop()

    def start(self):
        self._uistack.push(World(self._uistack))

    def tectonics(self):
        self._uistack.push(Tectonics(self._uistack))

    def climate(self):
        self._uistack.push(Climate(self._uistack))

    def rivers(self):
        self._uistack.push(Rivers(self._uistack))

    def erosion(self):
        self._uistack.push(Erosion(self._uistack))

    def population(self):
        self._uistack.push(Population(self._uistack))

    def racination(self):
        self._uistack.push(Racination(self._uistack))

    def prehistory(self):
        self._uistack.push(Prehistory(self._uistack))

    def split(self):
        self._uistack.push(Split(self._uistack))

    def move(self):
        self._uistack.push(Move(self._uistack))

    def options(self):
        self._uistack.push(Options(self._uistack))
