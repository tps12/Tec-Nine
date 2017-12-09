import random

from language.breaking import break_vowels
from language.lexicon import lexicon
from language.metaphony import a_mutate, i_mutate
from language.phonemes import phonemes

def generate():
    vs, cs = phonemes()
    return list(lexicon(vs, cs, random.gauss(0.5, 0.1), random.gauss(0.5, 0.1), 2000))

def mutate(origins, fn):
    shuffled = list(origins)
    random.shuffle(shuffled)
    mutations = {}
    for origin in shuffled:
        if origin in mutations:
            continue
        word = fn(origin)
        if word != origin:
            mutations[origin] = word
    return [mutations[origin] if origin in mutations else origin for origin in origins]

def amutate(origins):
    return mutate(origins, a_mutate)

def imutate(origins):
    return mutate(origins, a_mutate)

def breakvowels(origins):
    return mutate(origins, break_vowels)
