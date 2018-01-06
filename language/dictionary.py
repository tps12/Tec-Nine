class Dictionary(object):
    def __init__(self):
        self._words = {}
        self._defwords = {}

    def add(self, word, kind, index):
        if self.defines(word):
            raise ValueError("Can't duplicate word")
        if self.describes(kind, index):
            raise ValueError("Can't duplicate definition")
        defn = (kind, index)
        self._worddefs[word] = defn
        self._defwords[defn] = word

    def rename(self, old, new):
        self.add(new, *self.popword(old))

    def popword(self, word):
        defn = self._worddefs.pop(word)
        del self._defwords[defn]
        return defn

    def popdef(self, kind, index):
        word = self._defwords.pop((kind, index))
        del self._worddefs[word]
        return word

    def define(self, word):
        return self._worddefs[word]

    def describe(self, kind, index):
        return self._defwords[(kind, index)]

    def defines(self, word):
        return word in self._worddefs

    def describes(self, kind, index):
        return (kind, index) in self._defwords

    def lexicon(self):
        return self._worddefs.keys()

    def defs(self):
        return self._defwords.keys()
