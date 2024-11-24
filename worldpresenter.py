from nicegui import run, ui

import math
import random

from formatpopulation import popstr
from planetdata import Data
from worlddisplay import WorldDisplay
from worldsimulation import WorldSimulation

climatenames = {
    u'BW': 'desert',
    u'BS': 'steppe',
    u'Af': 'rainforest',
    u'Am': 'monsoon',
    u'Aw': 'savanna',
    u'Cf': 'temperate',
    u'Cs': 'temperate, dry summer',
    u'Cw': 'temperate, dry winter',
    u'Df': 'cold',
    u'Ds': 'cold, dry summer',
    u'Dw': 'cold, dry winter',
    u'ET': 'tundra',
    u'EF': 'ice cap' }

# Return a random value from the given spin box, favoring m (twice as likely to
# return m as either the min or max, with probability sloping on either side).
def randomspinvalue(b, m):
    r = range(b.min, b.max + b.props['step'], b.props['step'])
    pw = 0
    ws = []
    for v in r:
        dw = float(v - r[0])/(m - r[0]) if v < m else float(r[-1] - v)/(r[-1] - m)
        w = pw + (1 + dw)
        ws.append(w)
        pw = w
    f = random.uniform(0, pw)
    for i in range(len(r)):
        if f < ws[i]:
            return r[i]

def randomticks():
    n = 0
    while True:
        if random.random() < 0.05:
            return n
        n += 1

def randomtime():
    return WorldSimulation.tecdt * (1 + randomticks())

def created(radius, gridsize, dayhours, tilt, pangeasize, atmdt, lifedt, peopledt):
    return WorldSimulation().create(radius, gridsize, dayhours, tilt, pangeasize, atmdt, lifedt, peopledt).savedata()

def updated(model):
    model.update()
    return model.savedata()

class WorldPresenter(object):
    radii_and_grid_sizes = [
        (2100, 4),
        (3700, 5),
        (6400, 6),
        (11000, 7),
        (19000, 8)]
    day_hours = [8, 12, 24, 48]

    def __init__(self, view, uistack):
        self._view = view
        self._view.randomize.on_value_change(lambda event: self.randomized(event.value))
        self._view.create_new.on_click(self.create)
        self._view.start.on_click(self.start)
        self._view.pause.on_click(self.pause)
        self._view.done.on_click(self.done)
        self._view.load.on_click(self.load)
        self._view.save.on_click(self.save)

        self._uistack = uistack

        self._model = None
        self._view.randomize.set_value(True)
        self._view.start.disable()
        self._view.pause.set_visibility(False)

    def randomized(self, value):
        randomize = value
        for param in [self._view.spin, self._view.tilt, self._view.land, self._view.atmt, self._view.lifet, self._view.peoplet]:
            (param.disable if randomize else param.enable)()

    async def create(self, gridsize=None):
        if self._model is not None:
           self._view.content.clear()

        if self._view.randomize.value:
            # Randomize values, but favor Earth-like ones.
            self._view.spin.set_value(random.choice([0,1,1,2,2,2,3,3]))
            self._view.tilt.set_value(randomspinvalue(self._view.tilt, 23))
            self._view.land.set_value(randomspinvalue(self._view.land, 29))
            self._view.atmt.set_value(randomtime())
            self._view.lifet.set_value(randomtime())
            self._view.peoplet.set_value(randomtime())

        r, g = self.radii_and_grid_sizes[self._view.radius.value]
        land_r = math.sqrt(0.04 * self._view.land.value)

        self._model = WorldSimulation()
        self._model.loaddata(Data.loaddata(
            await run.cpu_bound(created, r, gridsize or g, self.day_hours[self._view.spin.value], self._view.tilt.value, land_r, self._view.atmt.value, self._view.lifet.value, self._view.peoplet.value)))
        self._view.years.text = self._model.years
        self._view.population.text = self._model.population

        with self._view.content:
          self._display = WorldDisplay(self._model, self.selecttile).style('display: flex').classes('flex-grow')

        self._view.rotate.value = self._display.rotate
        self._view.rotate.on_value_change(lambda event: self.rotate(event.value))

        self._view.aspect.set_value(self._display.aspect)
        self._view.aspect.on_value_change(lambda event: self.aspect(event.value))

        self._view.start.set_visibility(True)
        self._view.start.enable()
        self._view.pause.set_visibility(False)
        self._view.done.enable()

    def selecttile(self, tile):
        self._display.invalidate()
        self._view.content.update()
        self._view.details.clear()
        if tile is not None:
            populated = self._model.populated
            with self._view.details.parent_slot.parent:
                self._view.details.delete()
                self._view.details = ui.tree([
                    {'id': 'Layers', 'children': [{'id': layer.rock['name']} for layer in reversed(tile.layers)]}
                ] + ([
                    {'id': climatenames[tile.climate.koeppen]}
                ] if tile.elevation > 0 and tile.climate else [])
                 + ([
                    {'id': popstr(populated[tile][1])} # TODO: heritage
                ] if tile in populated else []), label_key='id')
#            rock = self._listitemclass(['Layers'])
#            for layer in reversed(tile.layers):
#                name = self._listitemclass([layer.rock['name']])
#                name.setToolTip(0, repr({ 'thickness': layer.thickness,
#                                          'rock': layer.rock }))
#                rock.addChild(name)
#            self._view.details.addTopLevelItem(rock)
#            if tile.elevation > 0 and tile.climate:
#                climate = self._listitemclass([climatenames[tile.climate.koeppen]])
#                climate.setToolTip(0, repr({ 'temperature': tile.climate.temperature,
#                                             'precipitation': tile.climate.precipitation }))
#                self._view.details.addTopLevelItem(climate)
#            populated = self._model.populated
#            if tile in populated:
#                heritage, count = populated[tile]
#                population = self._listitemclass([popstr(count)])
#                def ancestors(h, p):
#                    item = self._listitemclass([h.name])
#                    for a in h.ancestry or []:
#                        ancestors(a, item)
#                    p.addChild(item)
#                ancestors(heritage, population)
#                self._view.details.addTopLevelItem(population)

    def rotate(self, value):
        if self._model is None: return
        self._display.rotate = value
        self._view.content.update()

    def aspect(self, value):
        if self._model is None: return
        self._display.aspect = value
        self._display.invalidate()
        self._view.content.update()

    def load(self):
        filename = QFileDialog.getOpenFileName(self._view,
                                               'Load simulation state',
                                               '',
                                               '*{0}'.format(Data.EXTENSION))[0]
        if len(filename) > 0:
            data = Data.load(filename)
            self.create(data['gridsize'])
            self._model.loaddata(data)
            self._view.content.update()
            self.tick()

    def save(self):
        if self._model is None: return
        filename = QFileDialog.getSaveFileName(self._view,
                                               'Save simulation state',
                                               '',
                                               '*{0}'.format(Data.EXTENSION))[0]
        if len(filename) > 0:
            self._model.save(filename)

    def done(self):
        if self._model is not None:
            self._worker.stop()
            self._worker.wait()
        self._uistack.pop()

    def started(self):
        self._view.start.setVisible(False)
        self._view.pause.setVisible(True)
        self._view.pause.setEnabled(True)
        self._view.done.setEnabled(False)

    def stopped(self):
        self._view.start.setVisible(True)
        self._view.start.setEnabled(True)
        self._view.pause.setVisible(False)
        self._view.done.setEnabled(True)

    async def start(self):
        if self._model is None: return
        self._view.start.set_visibility(False)
        self._view.pause.set_visibility(True)
        while self._view.pause.visible:
            self._model.loaddata(Data.loaddata(await run.cpu_bound(updated, self._model)))
            self._view.years.text = self._model.years
            self._view.population.text = self._model.population
            self._display.invalidate()

    def pause(self):
        if self._model is None: return
        self._view.pause.set_visibility(False)
        self._view.start.set_visibility(True)

    def tick(self):
        self._view.years.setText(self._model.years)
        self._view.population.setText(self._model.population)
        self._display.invalidate()
        self._view.content.update()
