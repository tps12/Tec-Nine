class Syllable(object):
    def __init__(self, onset, nucleus, coda):
        self.onset = onset
        self.nucleus = nucleus
        self.coda = coda

    @property
    def phonemes(self):
        return self.onset + self.nucleus + self.coda

    def __repr__(self):
        return ''.join(self.phonemes)

    def __eq__(self, other):
        return self.phonemes == other.phonemes

    def __hash__(self):
        return hash((tuple(self.phonemes)))

class Word(object):
    def __init__(self, syllables):
        self.syllables = syllables

    @property
    def phonemes(self):
        return [p for s in self.syllables for p in s.phonemes]

    def __repr__(self):
        return '\u00b7'.join([repr(s) for s in self.syllables])

    def __eq__(self, other):
        return self.syllables == other.syllables

    def __hash__(self):
        return hash(tuple(self.syllables))
