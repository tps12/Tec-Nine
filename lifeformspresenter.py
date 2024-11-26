from nicegui import ui

import pickle

from lifeformsdisplay import LifeformsDisplay
from lifeformssimulation import LifeformsSimulation
from planetdata import Data

class LifeformsPresenter(object):
    def __init__(self, view, on_done):
        self._view = view
        self._view.load.on_click(self.load)
        self._view.done.on_click(on_done)

        self._model = None

    def set_model_state(self, data):
        self._model = LifeformsSimulation()
        self._model.loaddata(Data.loaddata(data))

        with self._view.content:
            self._display = LifeformsDisplay(self._model, self.selecttile).style('display: flex').classes('flex-grow')

        self._view.attribute.set_value(self._display.shownattribute)
        self._view.attribute.on_value_change(lambda event: self.showattribute(event.value))

        self._view.season.on_value_change(lambda event: self.season(event.value))

        self._view.glaciation.on_value_change(lambda event: self.glaciation(event.value))

        self._view.rotate.value = self._display.rotate
        self._view.rotate.on_value_change(lambda event: self.rotate(event.value))

    def selecttile(self, tile):
        selected = None
        selectedspecies = self._display.selectedspecies
        self._display.invalidate()
        self._view.content.update()
        self._view.details.clear()
        if tile is not None:
            for f, t in self._model.tiles.items():
                if t is tile:
                    species = []
                    for i in LifeformsDisplay.attributeindices[self._display.shownattribute]:
                        t = self._model.species()[i]
                        if f not in t:
                            continue
                        pop = t[f]
                        species += [s for s in pop[self._display.season]]
                    self.detailspecies = sorted(species, key=lambda s: s.name)
                    for s in self.detailspecies:
                        with self._view.details:
                            item = ui.item(s.name, on_click=lambda: self.currentdetail(s))
                        if s == selectedspecies:
                            selected = item
                    break
        self.currentdetail(selectedspecies if selected is not None else None)

    def currentdetail(self, s):
        if s == self._display.selectedspecies:
            return
        self._display.selectedspecies = s
        self._display.invalidate()
        self._view.content.update()

    def rotate(self, value):
        if self._model is None: return
        self._display.rotate = value
        self._view.content.update()

    def showattribute(self, value):
        if self._model is None: return
        self._display.shownattribute = value
        self._display.selectedspecies = None
        self._display.invalidate()
        self._view.content.update()
        self.selecttile(self._display.selected)

    def season(self, value):
        if self._model is None: return
        self._display.season = int(round((len(self._model.seasons)-1) * value/100.0))
        self._display.invalidate()
        self._view.content.update()
        self.selecttile(self._display.selected)

    def glaciation(self, _):
        if self._model is None: return
        glaciation = 1 - self._view.glaciation.value/100
        if self._model.glaciation == glaciation:
            return
        self._model.glaciation = glaciation
        self._display.invalidate()
        self._view.content.update()
        self.selecttile(self._display.selected)

    async def load(self):
        def load(event):
            self.set_model_state(pickle.loads(event.content.read()))
            dialog.close()

        with ui.dialog() as dialog, ui.card():
            ui.upload(on_upload=load)
        await dialog

