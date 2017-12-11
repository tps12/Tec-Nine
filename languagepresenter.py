import random

import language.metaphony
import language.output
import languagesimulation

class LanguagePresenter(object):
    def __init__(self, view, uistack, listitemclass):
        self._view = view

        self._view.generate.clicked.connect(self.generate)
        self._view.amutate.clicked.connect(self.amutate)
        self._view.imutate.clicked.connect(self.imutate)
        self._view.breakvowels.clicked.connect(self.breakvowels)
        self._view.leniteopen.clicked.connect(self.open)
        self._view.sonorize.clicked.connect(self.sonorize)
        self._view.vocalize.clicked.connect(self.vocalize)

        self._uistack = uistack
        self._listitemclass = listitemclass

        self.generate()

    def _populate(self):
        self._view.source.clear()
        for word in self._model[0]:
            item = self._listitemclass(language.output.write(word))
            item.setToolTip('/{}/'.format(language.output.pronounce(word)))
            self._view.source.addItem(item)
        self._view.dest.clear()
        for i in range(len(self._model[1])):
            origin, word = [m[i] for m in self._model]
            item = self._listitemclass(language.output.write(word))
            item.setToolTip('/{}/'.format(language.output.pronounce(word)))
            if word != origin:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            self._view.dest.addItem(item)

    def generate(self):
        self._model = (sorted(languagesimulation.generate(), key=language.output.write), [])
        self._populate()

    def apply(self, fn):
        origins = self._model[1] or self._model[0]
        words = fn(origins)
        if words != origins:
            self._model = tuple([[values[i] for i in sorted(range(len(values)), key=lambda i: language.output.write(origins[i]))]
                                  for values in (origins, words)])
        else:
            self._model = ([words[i] for i in sorted(range(len(words)), key=lambda i: language.output.write(words[i]))], [])
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
