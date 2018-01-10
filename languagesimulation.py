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

def search(initgens, yieldfn):
    gens = [initgen() for initgen in initgens]
    outputs = [next(g) for g in gens]
    while True:
        yield yieldfn(outputs)
        for i in range(len(gens)):
            try:
                outputs[i] = next(gens[i])
                break
            except StopIteration:
                gens[i] = initgens[i]()
                outputs[i] = next(gens[i])
        else:
            break

def adaptcluster(ps, gen, src):
    yield from search([(lambda p: lambda: gen(p, src))(phoneme) for phoneme in ps], lambda qs: qs)

def adaptsyllable(syllable, vs, cs):
    yield from search([(lambda args: lambda: adaptcluster(*args))(arguments)
                       for arguments in [
                           (syllable.onset, language.phonemes.nearestconsonants, cs),
                           (syllable.nucleus, language.phonemes.nearestvowels, vs),
                           (syllable.coda, language.phonemes.nearestconsonants, cs)]],
                      lambda ps: language.words.Syllable(*ps))

def adaptsounds(word, vs, cs, stress):
    yield from search([(lambda s: lambda: adaptsyllable(s, vs, cs))(syllable) for syllable in word.syllables],
                      lambda ss: language.words.Word(ss, stress))

def constrain(word, constraints, vs, stress):
    filler = language.phonotactics.filler(vs)
    yield from search([(lambda s: lambda: language.phonotactics.constrain(s, constraints, filler))(syllable)
                       for syllable in word.syllables],
                      lambda ss: language.words.Word([s for g in ss for s in g], stress))
