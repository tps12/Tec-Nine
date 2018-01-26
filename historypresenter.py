from PySide.QtCore import Qt
from PySide.QtGui import QGridLayout, QFileDialog

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

class HistoryPresenter(object):
    def __init__(self, view, uistack, listitemclass):
        self._view = view
        self._view.start.clicked.connect(self.start)
        self._view.pause.clicked.connect(self.pause)
        self._view.step.clicked.connect(self.step)
        self._view.load.clicked.connect(self.load)
        self._view.save.clicked.connect(self.save)
        self._view.done.clicked.connect(self.done)

        self._model = HistorySimulation(6, True)
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
                self._display.selectnations(selected, self._model.nationtradepartners(selected), self._model.nationconflictrivals(selected))
                break
        self._display.invalidate()
        self._view.content.update()
        self._view.details.clear()
        if selected is not None:
            lang = self._model.language(selected)
            word = lang.describe('nation', selected)
            name = self._listitemclass([capitalize(language.output.write(word))])
            name.setToolTip(0, '/{}/'.format(language.output.pronounce(word)))
            self._view.details.addTopLevelItem(name)

            tradepartners = self._model.nationtradepartners(selected)
            if tradepartners:
                trade = self._listitemclass(['Trade'])
                partners = self._listitemclass(['Partners'])
                for partner in tradepartners:
                    if lang.describes('nation', partner):
                        word = lang.describe('nation', partner)
                    else:
                        word = self._model.language(partner).describe('nation', partner)
                    text = capitalize(language.output.write(word))
                    tip = '/{}/'.format(language.output.pronounce(word))
                    original = self._model.language(partner).describe('nation', partner)
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
                        text, tip = self._model.resource(kind, index).name, None
                        if lang.describes(kind, index):
                            word = lang.describe(kind, index)
                            text += ' ({})'.format(language.output.write(word))
                            tip = '/{}/'.format(language.output.pronounce(word))
                        values.append((text, tip))
                    for (text, tip) in sorted(values):
                        name = self._listitemclass([text])
                        if tip is not None:
                            name.setToolTip(0, tip)
                        item.addChild(name)
                    trade.addChild(item)

                self._view.details.addTopLevelItem(trade)

            conflictrivals = self._model.nationconflictrivals(selected)
            if conflictrivals:
                conflict = self._listitemclass(['Conflict'])
                rivals = self._listitemclass(['Rivals'])
                for rival in conflictrivals:
                    if lang.describes('nation', rival):
                        word = lang.describe('nation', rival)
                    else:
                        word = self._model.language(rival).describe('nation', rival)
                    text = capitalize(language.output.write(word))
                    tip = '/{}/'.format(language.output.pronounce(word))
                    original = self._model.language(rival).describe('nation', rival)
                    if language.output.write(original) != language.output.write(word):
                        text += ' ({})'.format(capitalize(language.output.write(original)))
                    if language.output.pronounce(original) != language.output.pronounce(word):
                        tip += ' (/{}/)'.format(language.output.pronounce(original))
                    name = self._listitemclass([text])
                    name.setToolTip(0, tip)
                    rivals.addChild(name)
                conflict.addChild(rivals)
                self._view.details.addTopLevelItem(conflict)

            wordlist = self._listitemclass(['Language'])
            for word in sorted(lang.lexicon(), key=language.output.write):
                (kind, index) = lang.define(word)
                name = language.output.write(word)
                text = '{} (/{}/): {}'.format(capitalize(name) if kind is 'nation' else name,
                                              language.output.pronounce(word),
                                              'nation' if kind == 'nation' else self._model.resource(kind, index).name)
                wordlist.addChild(self._listitemclass([text]))
            self._view.details.addTopLevelItem(wordlist)

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
