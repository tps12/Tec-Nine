import random

from language.breaking import break_vowels
import language.elision
import language.lenition
from language.lexicon import lexicon
from language.metaphony import a_mutate, i_mutate
from language.phonemes import phonemes
import language.phonotactics
from language.stats import Language

def generate():
    vs, cs = phonemes()
    return Language(lexicon(vs, cs, round(random.gauss(-0.5, 1)), random.gauss(0.5, 0.1), random.gauss(0.5, 0.1), None, 2000))

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

def apheresize(origins):
    return mutate(origins, language.elision.apheresize)

def syncopate(origins):
    return mutate(origins, language.elision.syncopate)

def apocopate(origins):
    return mutate(origins, language.elision.apocopate)

soundchanges = [
    a_mutate,
    i_mutate,
    break_vowels,
    language.lenition.open,
    language.lenition.sonorize,
    language.lenition.vocalize,
    language.elision.apheresize,
    language.elision.syncopate,
    language.elision.apocopate]

def adaptcluster(ps, gen, src):
    reset = lambda i: gen(ps[i], src)
    gens = [reset(i) for i in range(len(ps))]
    qs = [next(g) for g in gens]
    while True:
        yield qs
        i = len(gens) - 1
        while i >= 0:
            try:
                qs[i] = next(gens[i])
                break
            except StopIteration:
                gens[i] = reset(i)
                qs[i] = next(gens[i])
                i -= 1
        else:
            break

def adaptsyllable(syllable, vs, cs):
    reset = lambda i: [adaptcluster(syllable.onset, language.phonemes.nearestconsonants, cs),
                       adaptcluster(syllable.nucleus, language.phonemes.nearestvowels, vs),
                       adaptcluster(syllable.coda, language.phonemes.nearestconsonants, cs)][i]
    gens = [reset(i) for i in range(3)]
    ps = [next(g) for g in gens]
    while True:
        yield language.words.Syllable(*ps)
        i = len(gens) - 1
        while i >= 0:
            try:
                ps[i] = next(gens[i])
                break
            except StopIteration:
                gens[i] = reset(i)
                ps[i] = next(gens[i])
                i -= 1
        else:
            break

def adaptsounds(word, vs, cs, stress):
    reset = lambda i: adaptsyllable(word.syllables[i], vs, cs)
    gens = [reset(i) for i in range(len(word.syllables))]
    ss = [next(g) for g in gens]
    while True:
        yield language.words.Word(ss, stress)
        i = len(gens) - 1
        while i >= 0:
            try:
                ss[i] = next(gens[i])
                break
            except StopIteration:
                gens[i] = reset(i)
                ss[i] = next(gens[i])
                i -= 1
        else:
            break

def constrain(word, constraints, vs, stress):
    filler = language.phonotactics.filler(vs)
    reset = lambda i: language.phonotactics.constrain(word.syllables[i], constraints, filler)
    gens = [reset(i) for i in range(len(word.syllables))]
    ss = [next(g) for g in gens]
    while True:
        yield language.words.Word([s for g in ss for s in g], stress)
        i = len(gens) - 1
        while i >= 0:
            try:
                ss[i] = next(gens[i])
                break
            except StopIteration:
                gens[i] = reset(i)
                ss[i] = next(gens[i])
                i -= 1
        else:
            break
