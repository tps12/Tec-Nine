class Origin(object):
    def __init__(self, word, language, origin=None):
        self.word = word
        self.language = language
        self.origin = origin

    def ultimate(self):
        return self if self.origin is None else self.origin.ultimate()

    def pedigree(self):
        if self.origin is None:
            return [self.language]
        pedigree = self.origin.pedigree()
        if self.language[0] == pedigree[0][0]:
            return pedigree
        return [self.language] + pedigree

class Dictionary(object):
    def __init__(self):
        self._worddefs = {}
        self._defwords = {}
        self._origins = {}

    def add(self, word, kind, index, origin):
        if self.defines(word):
            raise ValueError("Can't duplicate word")
        if self.describes(kind, index):
            raise ValueError("Can't duplicate definition")
        defn = (kind, index)
        self._worddefs[word] = defn
        self._defwords[defn] = word
        self._origins[word] = origin

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

    def origin(self, word):
        return self._origins[word]
