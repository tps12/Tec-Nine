from nicegui import app, ui
from nicegui.elements.column import Column
from mainmenupresenter import MainMenuPresenter

class MainMenu(Column):
    def __init__(self, on_create, on_done):
        super().__init__()
        with self.style('flex: auto; align-items: center'):
            self.start = ui.button('Start')
            self.tectonics = ui.button('Tectonics')
            self.terrain = ui.button('Terrain')
            self.history = ui.button('History')
            self.language = ui.button('Language')
            self.climate = ui.button('Climate')
            self.rivers = ui.button('Rivers')
            self.erosion = ui.button('Erosion')
            self.population = ui.button('Population')
            self.lifeforms = ui.button('Flora and Fauna')
            self.racination = ui.button('Racination')
            self.prehistory = ui.button('Prehistory')
            self.split = ui.button('Split')
            self.movepoints = ui.button('Move')
        MainMenuPresenter(self, on_create, on_done)
