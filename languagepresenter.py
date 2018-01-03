import random

import language.ipa
import language.metaphony
import language.output
import language.phonemes
import languagesimulation

class LanguagePresenter(object):
    def __init__(self, view, uistack, listitemclass):
        self._view = view

        self._view.generate.clicked.connect(self.generate)
        self._view.borrow.clicked.connect(self.borrow)
        self._view.amutate.clicked.connect(self.amutate)
        self._view.imutate.clicked.connect(self.imutate)
        self._view.breakvowels.clicked.connect(self.breakvowels)
        self._view.leniteopen.clicked.connect(self.open)
        self._view.sonorize.clicked.connect(self.sonorize)
        self._view.vocalize.clicked.connect(self.vocalize)
        self._view.apheresize.clicked.connect(self.apheresize)
        self._view.syncopate.clicked.connect(self.syncopate)
        self._view.apocopate.clicked.connect(self.apocopate)

        self._uistack = uistack
        self._listitemclass = listitemclass

        self.generate()

    def _populate(self):
        self._view.source.clear()
        for i in range(len(self._model[0].lexicon)):
            source, word = [m.lexicon[i] for m in self._model[0:2]]
            item = self._listitemclass(language.output.write(word))
            tip = '/{}/'.format(language.output.pronounce(word))
            if word != source:
                tip += ' ({}, /{}/)'.format(language.output.write(source), language.output.pronounce(source))
            item.setToolTip(tip)
            self._view.source.addItem(item)
        self._view.sourcephonemes.setText(', '.join([language.ipa.ipa[v] for v in language.phonemes.vowels if v in self._model[1].vowels] +
                                                    [language.ipa.ipa[c] for c in language.phonemes.consonants if c in self._model[1].consonants]))
        self._view.dest.clear()
        for i in range(len(self._model[2].lexicon)):
            source, origin, word = [m.lexicon[i] for m in self._model]
            item = self._listitemclass(language.output.write(word))
            tip = '/{}/'.format(language.output.pronounce(word))
            if word != source:
                tip += ' ({}, /{}/)'.format(language.output.write(source), language.output.pronounce(source))
            item.setToolTip(tip)
            if word != origin:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            self._view.dest.addItem(item)
        self._view.destphonemes.setText(', '.join([language.ipa.ipa[v] for v in language.phonemes.vowels if v in self._model[2].vowels] +
                                                  [language.ipa.ipa[c] for c in language.phonemes.consonants if c in self._model[2].consonants]))

    def generate(self):
        origins = languagesimulation.generate()
        origins.sort(lambda i: language.output.write(origins.lexicon[i]))
        self._model = (origins, languagesimulation.Language(origins.lexicon), languagesimulation.Language([]))
        self._populate()

    def borrow(self):
        lang = languagesimulation.generate()
        for _ in range(3):
            lang = languagesimulation.mutate(lang, random.choice(languagesimulation.soundchanges))
        source = list(lang.lexicon)
        random.shuffle(source)
        borrowed = source[0]
        origins = self._model[2] if self._model[2].lexicon else self._model[1]
        words = languagesimulation.Language(origins.lexicon)
        adapted = languagesimulation.adaptsounds(borrowed, words.vowels, words.consonants, words.stress)
        constrained = languagesimulation.constrain(adapted, words.constraints, words.vowels, words.stress)

        text = language.output.write(borrowed)
        tip = '/{}/'.format(language.output.pronounce(borrowed))
        if adapted != borrowed:
            text += '\u2192{}'.format(language.output.write(adapted))
            tip += '\u2192/{}/'.format(language.output.pronounce(adapted))
        if constrained != adapted:
            text += '\u2192{}'.format(language.output.write(constrained))
            tip += '\u2192/{}/'.format(language.output.pronounce(constrained))

        self._model[0].lexicon.append(borrowed)
        origins.lexicon.append(borrowed)
        words.lexicon.append(constrained)
        sortkey = lambda i: language.output.write(words.lexicon[i])
        self._model = self._model[0], origins, words
        for m in self._model:
            m.sort(sortkey)
        self._populate()
        self._view.borrowed.setText(text)
        self._view.borrowed.setToolTip(tip)

    def apply(self, fn):
        origins = self._model[2] if self._model[2].lexicon else self._model[1]
        words = fn(origins)
        sortkey = lambda i: language.output.write(words.lexicon[i])
        self._model = self._model[0], origins, words if words != origins else languagesimulation.Language([])
        if words.lexicon:
            for m in self._model:
                m.sort(sortkey)
        self._populate()

    def amutate(self):
        self.apply(languagesimulation.amutate)

    def imutate(self):
        self.apply(languagesimulation.imutate)

    def breakvowels(self):
        self.apply(languagesimulation.breakvowels)

    def open(self):
        self.apply(languagesimulation.leniteopen)

    def sonorize(self):
        self.apply(languagesimulation.lenitesonorize)

    def vocalize(self):
        self.apply(languagesimulation.lenitevocalize)

    def apheresize(self):
        self.apply(languagesimulation.apheresize)

    def syncopate(self):
        self.apply(languagesimulation.syncopate)

    def apocopate(self):
        self.apply(languagesimulation.apocopate)
