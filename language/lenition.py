import random

from .phonemes import vowels
from .words import Syllable, Word

def open(word):
    lenited = {
        'pp': ['p'],
        'tt': ['t'],
        'kk': ['k'],
        'p': ['pP', 'pf'],
        't': ['tT', 'ts'],
        'k': ['kx'],
        'pP': ['P'],
        'pf': ['f'],
        'tT': ['T'],
        'ts': ['s'],
        'kx': ['x'],
        'P': ['h'],
        'f': ['h'],
        'T': ['h'],
        's': ['h'],
        'x': ['h'],
        'h': ['']}
    for i in range(len(word.syllables)):
        if word.syllables[i].nucleus and i < len(word.syllables)-1 and word.syllables[i+1].nucleus:
            seq = ''.join([''.join(c) for c in (word.syllables[i].coda, word.syllables[i+1].onset) if c])
            if seq in lenited:
                l = random.choice(lenited[seq])
                if len(l) == 0:
                    a, b = (Syllable(word.syllables[i].onset, word.syllables[i].nucleus, []),
                            Syllable([], word.syllables[i+1].nucleus, word.syllables[i+1].coda))
                elif len(l) == 1:
                    a, b = (Syllable(word.syllables[i].onset, word.syllables[i].nucleus, []),
                            Syllable([l[0]], word.syllables[i+1].nucleus, word.syllables[i+1].coda))
                elif len(l) == 2:
                    a, b = (Syllable(word.syllables[i].onset, word.syllables[i].nucleus, [l[0]]),
                            Syllable([l[1]], word.syllables[i+1].nucleus, word.syllables[i+1].coda))
                else:
                    import pdb; pdb.set_trace()
                    raise ValueError('Did not expect lenition to {}-length sequence'.format(len(l)))
                return Word(word.syllables[:i] +
                            [a, b] +
                            word.syllables[i+2:],
                            word.stress)
    return word

def sonorize(word):
    lenited = {
        'p': ['b'],
        't': ['d'],
        'k': ['g'],
        'b': ['B', 'v'],
        'd': ['D', 'z', '*'],
        'g': ['Q'],
        'v': ['w'],
        'z': ['*'],
        'Q': ['w', 'j'],
        'B': [''],
        'w': [''],
        'D': [''],
        '*': [''],
        'j': ['']}
    for i in range(len(word.syllables)):
        if word.syllables[i].nucleus and i < len(word.syllables)-1 and word.syllables[i+1].nucleus:
            seq = ''.join([''.join(c) for c in (word.syllables[i].coda, word.syllables[i+1].onset) if c])
            if seq in lenited:
                l = random.choice(lenited[seq])
                if len(l) == 0:
                    a, b = (Syllable(word.syllables[i].onset, word.syllables[i].nucleus, []),
                            Syllable([], word.syllables[i+1].nucleus, word.syllables[i+1].coda))
                else:
                    a, b = (Syllable(word.syllables[i].onset, word.syllables[i].nucleus, []),
                            Syllable([l], word.syllables[i+1].nucleus, word.syllables[i+1].coda))
                return Word(word.syllables[:i] +
                            [a, b] +
                            word.syllables[i+2:],
                            word.stress)
    return word

def vocalize(word):
    lenited = {
        'l': ['w', 'j'],
        'w': ['u-'],
        'j': ['i']}
    for i in range(len(word.syllables)):
        if word.syllables[i].nucleus and i < len(word.syllables)-1 and word.syllables[i+1].nucleus:
            seq = ''.join([''.join(c) for c in (word.syllables[i].coda, word.syllables[i+1].onset) if c])
            if seq in lenited:
                l = random.choice(lenited[seq])
                if l in vowels:
                    a, b = (Syllable(word.syllables[i].onset, word.syllables[i].nucleus, []),
                            Syllable([], [l] + word.syllables[i+1].nucleus, word.syllables[i+1].coda))
                else:
                    a, b = (Syllable(word.syllables[i].onset, word.syllables[i].nucleus, []),
                            Syllable([l], word.syllables[i+1].nucleus, word.syllables[i+1].coda))
                return Word(word.syllables[:i] +
                            [a, b] +
                            word.syllables[i+2:],
                            word.stress)
    return word
