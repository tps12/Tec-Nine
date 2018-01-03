from .phonemes import *
from .words import *

def moveback(syllable):
    v = syllable.nucleus[0]
    b, h = backness(v), height(v)
    if b < max([len(vs) for vs in vowelpositions])-1:
        b += 1
        return Syllable(syllable.onset,
                        [vowelpositions[h][b]] + syllable.nucleus[1:],
                        syllable.coda)
    else:
        return syllable

def break_vowels(word):
    for i in range(len(word.syllables)):
        if len(word.syllables[i].nucleus) == 1:
            vowel = word.syllables[i].nucleus[0]
            if i+1 in range(len(word.syllables)) and word.syllables[i+1].nucleus:
                back = backness(word.syllables[i+1].nucleus[0])
            elif word.syllables[i].coda:
                back = backness(word.syllables[i].coda[0])
            else:
                continue
            ab = moveback(word.syllables[i])
            if ab != word.syllables[i]:
                return Word(word.syllables[:i] +
                            [ab] +
                            word.syllables[i+1:],
                            word.stress)
    return word
