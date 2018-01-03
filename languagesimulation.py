import random

from language.breaking import break_vowels
import language.elision
import language.lenition
from language.lexicon import lexicon
from language.metaphony import a_mutate, i_mutate
from language.phonemes import phonemes
import language.phonotactics

class Language(object):
    def __init__(self, lexicon):
        self.lexicon = list(lexicon)
        self.vowels, self.consonants = set(), set()
        numsyllables = numonsets = numcodas = 0
        stresses = {}
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
            if word.stress not in stresses:
                stresses[word.stress] = 1
            else:
                stresses[word.stress] += 1
            if (word.stress - len(word.syllables)) not in stresses:
                stresses[word.stress - len(word.syllables)] = 1
            else:
                stresses[word.stress - len(word.syllables)] += 1
        self.onsetp, self.codap = [num/numsyllables if numsyllables > 0 else 0 for num in (numonsets, numcodas)]
        self.constraints = language.phonotactics.constraints(self.lexicon)
        self.stress = max(stresses.items(), key=lambda stresscount: stresscount[1])[0] if stresses else None

    def sort(self, key):
        self.lexicon = [self.lexicon[i] for i in sorted(range(len(self.lexicon)), key=key)]

    def __eq__(self, other):
        return self.lexicon == other.lexicon

    def __hash__(self):
        return hash((tuple(self.lexicon)))

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

def adaptsounds(word, vs, cs, stress):
    ss = []
    for s in word.syllables:
        o = []
        for p in s.onset:
            o.append(language.phonemes.nearestconsonant(p, cs))
        n = []
        for p in s.nucleus:
            n.append(language.phonemes.nearestvowel(p, vs))
        c = []
        for p in s.coda:
            c.append(language.phonemes.nearestconsonant(p, cs))
        ss.append(language.words.Syllable(o, n, c))
    return language.words.Word(ss, stress)

def constrain(word, constraints, vs, stress):
    filler = language.phonotactics.filler(vs)
    ss = []
    for syllable in word.syllables:
        ss += language.phonotactics.constrain(syllable, constraints, filler)
    return language.words.Word(ss, stress)
