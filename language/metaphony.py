from .phonemes import *
from .words import *

def front(syllable):
    v = syllable.nucleus[-1]
    b, h = backness(v), height(v)
    if b > 0:
        b -= 1
        return Syllable(syllable.onset,
                        syllable.nucleus[:-1] + [vowelpositions[h][b]],
                        syllable.coda)
    else:
        return syllable

def raisen(syllable):
    v = syllable.nucleus[-1]
    b, h = backness(v), height(v)
    if h < len(vowelpositions) - 1:
        h += 1
        return Syllable(syllable.onset,
                        syllable.nucleus[:-1] + [vowelpositions[h][b]],
                        syllable.coda)
    else:
        return syllable

def lower(syllable):
    v = syllable.nucleus[-1]
    b, h = backness(v), height(v)
    if h > 0:
        h -= 1
        return Syllable(syllable.onset,
                        syllable.nucleus[:-1] + [vowelpositions[h][b]],
                        syllable.coda)
    else:
        return syllable

def i_mutate(word):
    if len(word.syllables) > 1:
        for i in range(len(word.syllables)-2, -1, -1):
            a, b = word.syllables[i], word.syllables[i+1]
            if any([v in b.nucleus for v in ('i', 'i"')]):
                af = front(a)
                if af != a:
                    return Word(word.syllables[:i] +
                                [af] +
                                word.syllables[i+1:])
                ar = raisen(a)
                if ar != a:
                    return Word(word.syllables[:i] +
                                [ar] +
                                word.syllables[i+1:])
    return word

def a_mutate(word):
    if len(word.syllables) > 1:
        for i in range(len(word.syllables)-2, -1, -1):
            a, b = word.syllables[i], word.syllables[i+1]
            if any([height(v) == len(vowelpositions)-1 for v in b.nucleus]):
                al = lower(a)
                if al != a:
                    return Word(word.syllables[:i] +
                                [al] +
                                word.syllables[i+1:])
    return word
