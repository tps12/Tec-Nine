from nicegui import run, ui

import pickle

from formatpopulation import percents, popstr
from historydisplay import HistoryDisplay
from historysimulation import HistorySimulation
import language.output
from planetdata import Data

phasetext = {
    'uninit': 'Uninitialized',
    'species': 'Settling species...',
    'nations': 'Defining nations...',
    'langs': 'Creating languages...',
    'coasts': 'Populating coasts...',
    'sim': 'Simulating'
}

def capitalize(s):
    return s[0].upper() + s[1:]

def conjoin(items):
    if len(items) == 1:
        return items[0]
    return '{} and {}'.format(', '.join(items[:-1]), items[-1])

def updated(model):
    model.update()
    return model.savedata()

load_timing = lambda: HistorySimulation._timing.routine('loading state')

class HistoryPresenter(object):
    def __init__(self, view, on_done):
        self._view = view
        self._view.start.on_click(self.start)
        self._view.pause.on_click(self.pause)
        self._view.step.on_click(self.step)
        self._view.load.on_click(self.load)
        self._view.save.on_click(self.save)
        self._view.done.on_click(on_done)

        self._model = None
        self._ticks = 0

        self._display = None

    def set_model_state(self, data):
        self._model = HistorySimulation()
        self._model.create(6, False)
        timing = load_timing()
        self._model.loaddata(Data.loaddata(data), timing)
        timing.done()

        self._view.content.clear()
        with self._view.content:
            self._display = HistoryDisplay(self._model, self.selecttile).style('display: flex').classes('flex-grow')

        self._view.rotate.value = self._display.rotate
        self._view.rotate.on_value_change(lambda event: self.rotate(event.value))

        self._view.aspect.set_value(self._display.aspect)
        self._view.aspect.on_value_change(lambda event: self.aspect(event.value))

        self._view.rivers.set_value(self._display.rivers)
        self._view.rivers.on_value_change(lambda event: self.rivers(event.value))

        self._view.pause.set_visibility(False)
        self._ticks = 1
        self._view.ticks.set_text(str(self._ticks))

    def selecttile(self, tile):
        selected = None
        for f, t in self._model.tiles.items():
            if t is tile:
                selected = self._model.boundaries[f] if f in self._model.boundaries else None
                self._display.selectnations(selected, self._model.statetradepartners(selected), self._model.stateconflictrivals(selected))
                break
        self._display.invalidate()
        self._view.details.clear()
        if selected is not None:
            langcache = {}
            def getlang(index):
                if index not in langcache:
                    langcache[index] = self._model.language(index)
                return langcache[index]
            nations = self._model.demographics(selected)
            lang = getlang(nations[0].languages[0].language)
            word = lang.describe('state', selected)

            detail_nodes = [
                {'id': f'{capitalize(language.output.write(word))} (/{language.output.pronounce(word)}/)'}
            ]

            tradepartners = self._model.statetradepartners(selected)
            if tradepartners:
                trade = {'id': 'Trade', 'children': []}
                partners = {'id': 'Partners', 'children': []}
                for partner in tradepartners:
                    word = lang.describe('state', partner)
                    text = capitalize(language.output.write(word))
                    tip = '/{}/'.format(language.output.pronounce(word))

                    othernations = self._model.demographics(partner)
                    original = getlang(othernations[0].languages[0].language).describe('state', partner)
                    if language.output.write(original) != language.output.write(word):
                        text += ' ({})'.format(capitalize(language.output.write(original)))
                    if language.output.pronounce(original) != language.output.pronounce(word):
                        tip += ' (/{}/)'.format(language.output.pronounce(original))

                    name = self._listitemclass([text])
                    name.setToolTip(0, tip)
                    partners['children'].append({'id': f'{text} ({tip})', 'children': []})
                trade['children'].append(partners)

                for (heading, resourcesfn) in [('Imports', self._model.imports),
                                               ('Exports', self._model.exports)]:
                    item = {'id': heading, 'children': []}
                    values = []
                    resources = resourcesfn(selected).values()
                    for (kind, index) in set.union(*resources) if resources else set():
                        values.append(self._model.resource(kind, index).name)
                    for text in sorted(values):
                        name = self._listitemclass([text])
                        item['children'].append({'id': text, 'children': []})
                    trade['children'].append(item)

                detail_nodes.append(trade)

            conflictrivals = self._model.stateconflictrivals(selected)
            if conflictrivals:
                conflict = {'id': 'Conflict', 'children': []}
                rivals = {'id': 'Rivals', 'children': []}
                for rival in conflictrivals:
                    word = lang.describe('state', rival)
                    text = capitalize(language.output.write(word))
                    tip = '/{}/'.format(language.output.pronounce(word))
                    othernations = self._model.demographics(rival)
                    original = getlang(othernations[0].languages[0].language).describe('state', rival)
                    if language.output.write(original) != language.output.write(word):
                        text += ' ({})'.format(capitalize(language.output.write(original)))
                    if language.output.pronounce(original) != language.output.pronounce(word):
                        tip += ' (/{}/)'.format(language.output.pronounce(original))
                    rivals['children'].append({'id': f'{text} ({tip})', 'children': []})
                conflict['children'].append(rivals)
                detail_nodes.append(conflict)

            demolangs = {}
            nationalities = {'id': 'Nationalities', 'children': []}
            nationpops = percents([demo.thousands for demo in nations])
            for demo in nations:
                # name nationality using its majority language
                word = getlang(demo.languages[0].language).describe('nation', demo.nation)
                nationality = {'id': f'{capitalize(language.output.write(word))} (/{language.output.pronounce(word)}/)', 'children': []}
                
                pop = popstr(demo.thousands)
                nationality['children'].append(
                    {'id': 'Population: {}({})'.format((pop + ' ') if pop != '0' else '', next(nationpops)), 'children': []})
                languages = {'id': 'Languages', 'children': []}
                for demolang in demo.languages:
                    word = getlang(demolang.language).describe('language', demolang.language)
                    langtext = capitalize(language.output.write(word))
                    demolangs[demolang.language] = langtext
                    pop = popstr(demolang.thousands)
                    langname = {
                        'id': '{} (/{}/): {}'.format(langtext, language.output.pronounce(word), pop)
                              if len(demo.languages) > 1 and pop != '0' else langtext,
                        'children': []
                    }
                    languages['children'].append(langname)
                nationality['children'].append(languages)

                nationalities['children'].append(nationality)
            detail_nodes.append(nationalities)
                
            languages = {'id': 'Languages', 'children': []}
            for (lang_index, _) in sorted(demolangs.items(), key=lambda langnames: langnames[1]):
                lang = getlang(lang_index)
                word = lang.describe('language', lang_index)
                wordlist = {'id': f'{capitalize(language.output.write(word))} (/{language.output.pronounce(word)}/)', 'children': []}

                for word in sorted(lang.lexicon(), key=language.output.write):
                    (kind, index) = lang.define(word)
                    name = language.output.write(word)
                    text = '{} (/{}/): {}'.format(capitalize(name) if kind != 'species' else name,
                                                  language.output.pronounce(word),
                                                  kind if kind != 'species' else self._model.resource(kind, index).name)
                    entry = {'id': text, 'children': []}
                    wordorigin = lang.origin(word)
                    if wordorigin is not None:
                        ultimate = wordorigin.ultimate()
                        ultimateword = language.output.write(ultimate.word)
                        if ultimate.language[0] != lang_index:
                            origin = 'From {}'.format(capitalize(language.output.write(ultimate.language[1])))
                            if ultimateword != name:
                                origin += ' "{}"'.format(capitalize(ultimateword) if kind != 'species' else ultimateword)
                            via = wordorigin.pedigree()[1:-1]
                            if via:
                                origin += ' via {}'.format(conjoin([capitalize(language.output.write(l[1])) for l in via]))
                        elif ultimateword != name:
                            origin = 'From "{}"'.format(capitalize(ultimateword) if kind != 'species' else ultimateword)
                        else:
                            origin = None
                        if origin is not None:
                            entry['children'].append({'id': origin, 'children': []})
                    wordlist['children'].append(entry)
                languages['children'].append(wordlist)
            detail_nodes.append(languages)
            with self._view.details.parent_slot.parent:
                self._view.details.delete()
                self._view.details = ui.tree(detail_nodes, label_key='id')
                self._view.update()

    def rotate(self, value):
        if self._model is None: return
        self._display.rotate = value
        self._view.content.update()

    def aspect(self, value):
        if self._model is None: return
        self._display.aspect = value
        self._view.content.update()

    def rivers(self, value):
        if self._model is None: return
        self._display.rivers = value
        self._view.content.update()

    async def load(self):
        def load(event):
            self.set_model_state(pickle.loads(event.content.read()))
            dialog.close()

        with ui.dialog() as dialog, ui.card():
            ui.upload(on_upload=load)
        await dialog

    async def save(self):
        with ui.dialog() as dialog, ui.card():
            with ui.row():
                ui.label('File name:')
                filename = ui.input(' ', placeholder='Enter file name')
            def save():
                print(filename.value)
                dialog.submit(filename.value)
            ui.button('Save', on_click=save, icon='save')
        filename = await dialog
        if filename:
            self._model.save(f'{filename}{Data.EXTENSION}')

    async def start(self):
        if self._model is None: return
        self._view.start.set_visibility(False)
        self._view.pause.set_visibility(True)
        self._view.step.disable()
        while self._view.pause.visible:
            timing = load_timing()
            self._model.loaddata(Data.loaddata(await run.cpu_bound(updated, self._model)), timing)
            timing.done()
            self.tick()

    def pause(self):
        if self._model is None: return
        self._view.pause.set_visibility(False)
        self._view.start.set_visibility(True)
        self._view.step.enable()

    async def step(self):
        self._view.start.disable()
        timing = load_timing()
        self._model.loaddata(Data.loaddata(await run.cpu_bound(updated, self._model)), timing)
        timing.done()
        self.tick()
        self._view.start.enable()

    def tick(self):
        self._view.phase.set_text(phasetext[self._model.phase])
        self._ticks += 1
        self._view.ticks.set_text(str(self._ticks))
        self._display.invalidate()
