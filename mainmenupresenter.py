from climate import Climate
from erosion import Erosion
from history import History
from languageui import Language
from lifeforms import Lifeforms
from population import Population
from prehistory import Prehistory
from racination import Racination
from rivers import Rivers
from tectonics import Tectonics
from terrain import Terrain
from split import Split
from world import World
from move import Move

class MainMenuPresenter(object):
    def __init__(self, view, on_create, on_done):
        view.start.on_click(lambda: on_create(lambda: World(on_done)))
        view.tectonics.disable()
        view.terrain.disable()
        view.history.disable()
        view.language.disable()
        view.climate.disable()
        view.rivers.disable()
        view.erosion.disable()
        view.population.disable()
        view.lifeforms.on_click(lambda: on_create(lambda: Lifeforms(on_done)))
        view.racination.disable()
        view.prehistory.disable()
        view.split.disable()
        view.movepoints.disable()

