from PySide.QtCore import Qt
from PySide.QtGui import QGridLayout, QFileDialog

from formatpopulation import percents, popstr
from historydisplay import HistoryDisplay
from historysimulation import HistorySimulation
import language.output
from planetdata import Data
from simthread import SimThread

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

class HistoryPresenter(object):
    def __init__(self, view, uistack, listitemclass):
        self._view = view
        self._view.start.clicked.connect(self.start)
        self._view.pause.clicked.connect(self.pause)
        self._view.step.clicked.connect(self.step)
        self._view.load.clicked.connect(self.load)
        self._view.save.clicked.connect(self.save)
        self._view.done.clicked.connect(self.done)

        self._model = HistorySimulation(6, False)
        self._worker = SimThread(self._model)
        self._worker.tick.connect(self.tick)
        self._worker.simstarted.connect(self.started)
        self._worker.simstopped.connect(self.stopped)
        self._view.phase.setText(phasetext[self._model.phase])
        self._ticks = 0
        self._worker.start()

        self._display = HistoryDisplay(self._model, self.selecttile)

        self._view.content.setLayout(QGridLayout())
        self._view.content.layout().addWidget(self._display)

        self._view.rotate.setValue(self._display.rotate)
        self._view.rotate.sliderMoved.connect(self.rotate)

        self._view.aspect.setCurrentIndex(self._display.aspect)
        self._view.aspect.currentIndexChanged[int].connect(self.aspect)

        self._view.rivers.setCheckState(Qt.Checked if self._display.rivers else Qt.Unchecked)
        self._view.rivers.stateChanged.connect(self.rivers)

        self._view.pause.setVisible(False)

        self._listitemclass = listitemclass

        self._uistack = uistack

    def selecttile(self, tile):
        selected = None
        for f, t in self._model.tiles.items():
            if t is tile:
                selected = self._model.boundaries[f] if f in self._model.boundaries else None
                self._display.selectnations(selected, self._model.statetradepartners(selected), self._model.stateconflictrivals(selected))
                break
        self._display.invalidate()
        self._view.content.update()
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
            name = self._listitemclass([capitalize(language.output.write(word))])
            name.setToolTip(0, '/{}/'.format(language.output.pronounce(word)))
            self._view.details.addTopLevelItem(name)

            tradepartners = self._model.statetradepartners(selected)
            if tradepartners:
                trade = self._listitemclass(['Trade'])
                partners = self._listitemclass(['Partners'])
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
                    partners.addChild(name)
                trade.addChild(partners)

                for (heading, resourcesfn) in [('Imports', self._model.imports),
                                               ('Exports', self._model.exports)]:
                    item = self._listitemclass([heading])
                    values = []
                    resources = resourcesfn(selected).values()
                    for (kind, index) in set.union(*resources) if resources else set():
                        values.append(self._model.resource(kind, index).name)
                    for text in sorted(values):
                        name = self._listitemclass([text])
                        item.addChild(name)
                    trade.addChild(item)

                self._view.details.addTopLevelItem(trade)

            conflictrivals = self._model.stateconflictrivals(selected)
            if conflictrivals:
                conflict = self._listitemclass(['Conflict'])
                rivals = self._listitemclass(['Rivals'])
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
                    name = self._listitemclass([text])
                    name.setToolTip(0, tip)
                    rivals.addChild(name)
                conflict.addChild(rivals)
                self._view.details.addTopLevelItem(conflict)

            demolangs = {}
            nationalities = self._listitemclass(['Nationalities'])
            nationpops = percents([demo.thousands for demo in nations])
            for demo in nations:
                # name nationality using its majority language
                word = getlang(demo.languages[0].language).describe('nation', demo.nation)
                nationality = self._listitemclass([capitalize(language.output.write(word))])
                nationality.setToolTip(0, '/{}/'.format(language.output.pronounce(word)))
                
                pop = popstr(demo.thousands)
                nationality.addChild(self._listitemclass(
                    ['Population: {}({})'.format((pop + ' ') if pop != '0' else '', next(nationpops))]))
                languages = self._listitemclass(['Languages'])
                for demolang in demo.languages:
                    word = getlang(demolang.language).describe('language', demolang.language)
                    langtext = capitalize(language.output.write(word))
                    demolangs[demolang.language] = langtext
                    pop = popstr(demolang.thousands)
                    langname = self._listitemclass([
                        '{}: {}'.format(langtext, pop)
                        if len(demo.languages) > 1 and pop != '0' else langtext])
                    langname.setToolTip(0, '/{}/'.format(language.output.pronounce(word)))
                    languages.addChild(langname)
                nationality.addChild(languages)

                nationalities.addChild(nationality)
            self._view.details.addTopLevelItem(nationalities)
                
            languages = self._listitemclass(['Languages'])
            for (lang_index, _) in sorted(demolangs.items(), key=lambda langnames: langnames[1]):
                lang = getlang(lang_index)
                word = lang.describe('language', lang_index)
                wordlist = self._listitemclass([capitalize(language.output.write(word))])
                wordlist.setToolTip(0, '/{}/'.format(language.output.pronounce(word)))

                for word in sorted(lang.lexicon(), key=language.output.write):
                    (kind, index) = lang.define(word)
                    name = language.output.write(word)
                    text = '{} (/{}/): {}'.format(capitalize(name) if kind != 'species' else name,
                                                  language.output.pronounce(word),
                                                  kind if kind != 'species' else self._model.resource(kind, index).name)
                    entry = self._listitemclass([text])
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
                            entry.addChild(self._listitemclass([origin]))
                    wordlist.addChild(entry)
                languages.addChild(wordlist)
            self._view.details.addTopLevelItem(languages)

    def rotate(self, value):
        self._display.rotate = value
        self._view.content.update()

    def aspect(self, value):
        if self._model is None: return
        self._display.aspect = value
        self._display.invalidate()
        self._view.content.update()

    def rivers(self, state):
        self._display.rivers = state == Qt.Checked
        self._display.invalidate()
        self._view.content.update()

    def load(self):
        filename = QFileDialog.getOpenFileName(self._view,
                                               'Load simulation state',
                                               '',
                                               '*{0}'.format(Data.EXTENSION))[0]
        if len(filename) > 0:
            self._model.load(filename)
            self._view.phase.setText(phasetext[self._model.phase])
            self._display.invalidate()
            self._view.content.update()

    def save(self):
        filename = QFileDialog.getSaveFileName(self._view,
                                               'Save simulation state',
                                               '',
                                               '*{0}'.format(Data.EXTENSION))[0]
        if len(filename) > 0:
            self._model.save(filename)

    def done(self):
        self._uistack.pop()

    def started(self):
        self._view.start.setVisible(False)
        self._view.pause.setVisible(True)
        self._view.pause.setEnabled(True)
        self._view.step.setEnabled(False)
        self._view.done.setEnabled(False)

    def stopped(self):
        self._view.start.setVisible(True)
        self._view.start.setEnabled(True)
        self._view.pause.setVisible(False)
        self._view.step.setEnabled(True)
        self._view.done.setEnabled(True)

    def start(self):
        self._view.start.setEnabled(False)
        self._view.step.setEnabled(False)
        self._view.done.setEnabled(False)
        self._worker.simulate(True)

    def pause(self):
        self._view.pause.setEnabled(False)
        self._worker.simulate(False)

    def step(self):
        self._view.start.setEnabled(False)
        self._view.step.setEnabled(False)
        self._model.update()
        self.tick()
        self._view.start.setEnabled(True)
        self._view.step.setEnabled(True)

    def tick(self):
        self._view.phase.setText(phasetext[self._model.phase])
        if self._model.initialized:
            self._ticks += 1
        self._view.ticks.setNum(self._ticks)
        #self._view.races.setNum(self._model.peoples)
        self._display.invalidate()
        self._view.content.update()
