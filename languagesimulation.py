import random

from language.breaking import break_vowels
import language.lenition
from language.lexicon import lexicon
from language.metaphony import a_mutate, i_mutate
from language.phonemes import phonemes

class Language(object):
    def __init__(self, lexicon):
        self.lexicon = list(lexicon)
        self.vowels, self.consonants = set(), set()
        numsyllables = numonsets = numcodas = 0
        for word in lexicon:
            for syllable in word.syllables:
                for phoneme in syllable.onset:
                    self.consonants.add(phoneme)
                for phoneme in syllable.nucleus:
                    self.vowels.add(phoneme)
                for phoneme in syllable.coda:
                    self.consonants.add(phoneme)
                if syllable.onset:
                    numonsets += 1
                if syllable.coda:
                    numcodas += 1
                numsyllables += 1
        self.onsetp, self.codap = [num/numsyllables for num in (numonsets, numcodas)]

    def sort(self, key):
        self.lexicon = [self.lexicon[i] for i in sorted(range(len(self.lexicon)), key=key)]

    def __eq__(self, other):
        return self.lexicon == other.lexicon

    def __hash__(self):
        return hash((tuple(self.lexicon)))

def generate():
    vs, cs = phonemes()
    return Language(lexicon(vs, cs, random.gauss(0.5, 0.1), random.gauss(0.5, 0.1), 2000))

def mutate(origins, fn):
    shuffled = list(origins.lexicon)
    random.shuffle(shuffled)
    mutations = {}
    seen = set()
    for origin in shuffled:
        if origin in mutations:
            continue
        word = fn(origin)
        if word != origin and word not in seen:
            mutations[origin] = word
            seen.add(word)
        else:
            seen.add(origin)
    return Language([mutations[origin] if origin in mutations else origin for origin in origins.lexicon])

def amutate(origins):
    return mutate(origins, a_mutate)

def imutate(origins):
    return mutate(origins, a_mutate)

def breakvowels(origins):
    return mutate(origins, break_vowels)

def leniteopen(origins):
    return mutate(origins, language.lenition.open)

def lenitesonorize(origins):
    return mutate(origins, language.lenition.sonorize)

def lenitevocalize(origins):
    return mutate(origins, language.lenition.vocalize)
