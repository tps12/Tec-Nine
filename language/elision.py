import random

from .words import Syllable, Word

def apheresize(word):
    if word.stress != 0 and not word.syllables[0].onset:
        return Word([Syllable(word.syllables[0].coda + word.syllables[1].onset,
                              word.syllables[1].nucleus,
                              word.syllables[1].coda)] +
                    word.syllables[2:],
                    word.stress - 1)
    return word

def syncopate(word):
    unstressed = [i for i in range(len(word.syllables)) if i != word.stress]
    if unstressed:
        i = random.choice(unstressed)
        if (i == 0 and not word.syllables[i].onset) or (i == len(word.syllables)-1 and not word.syllables[i].coda):
            # handle through aheresis/apocape
            return word
        beginning, middle, end = word.syllables[:max(i-1, 0)], [], word.syllables[i+2:]
        onset, coda = word.syllables[i].onset, word.syllables[i].coda
        if i-1 >= 0:
            # no following syllable, include coda here
            suffix = onset if i+1 < len(word.syllables) else onset + coda
            middle.append(Syllable(word.syllables[i-1].onset, word.syllables[i-1].nucleus, word.syllables[i-1].coda + suffix))
        if i+1 < len(word.syllables):
            # no preceding syllable, include onset here
            prefix = coda if i-1 >= 0 else onset + coda
            middle.append(Syllable(prefix + word.syllables[i+1].onset, word.syllables[i+1].nucleus, word.syllables[i+1].coda))
        return Word(beginning + middle + end,
                    (word.stress - 1) if word.stress > i else word.stress)
    return word

def apocopate(word):
    if word.stress != len(word.syllables) - 1 and not word.syllables[-1].coda:
        return Word(word.syllables[:-2] +
                    [Syllable(word.syllables[-2].onset,
                              word.syllables[-2].nucleus,
                              word.syllables[-2].coda + word.syllables[-1].onset)],
                    word.stress)
    return word
