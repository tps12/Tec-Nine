import random

import languagesimulation
import language.dictionary
import language.lexicon
import language.phonemes
import language.stats
import language.words

def borrow(word, stats, existing):
    for adapted in languagesimulation.adaptsounds(word, stats.vowels, stats.consonants, stats.stress):
        for borrowed in languagesimulation.constrain(adapted, stats.constraints, stats.vowels, stats.stress):
            if borrowed not in existing:
                return borrowed
    # nothing unique yet, try adding a new suffix
    for adapted in languagesimulation.adaptsounds(word, stats.vowels, stats.consonants, stats.stress):
        for borrowed in languagesimulation.constrain(adapted, stats.constraints, stats.vowels, stats.stress):
            borrowed = language.words.Word(
                borrowed.syllables +
                    language.lexicon.lexicon(list(stats.vowels), list(stats.consonants), 0, stats.onsetp, stats.codap, stats.constraints, 1).pop().syllables,
                stats.stress)
            if borrowed not in existing:
                return borrowed
    raise Exception("Couldn't borrow {}".format(word))  # TODO: handle

def reify(langs, index, ticks, borrowsubset, timing, indent):
    (conceptlist, soundchanges, neologisms, loans) = (
        langs[index]._concepts, langs[index]._changes, langs[index]._neologisms, langs[index]._loans)
    concept_words = {}
    existing = set()
    for t in range(ticks):
        timing.start('{}applying sound changes'.format(indent))
        changes = soundchanges[t]
        for i in range(len(changes)):
            concept = conceptlist[i]
            if concept not in concept_words:
                continue
            original = concept_words[concept]
            changed = languagesimulation.soundchanges[changes[i]](original)
            if changed != original and changed not in existing:
                concept_words[concept] = changed
                existing.remove(original)
                existing.add(changed)

        stats = None
        if t in neologisms:
            timing.start('{}coining words'.format(indent))
            for (coinage_state, concept_indices) in neologisms[t]:
                random.setstate(coinage_state)
                if concept_words:
                    stats = language.stats.Language(concept_words.values())
                    (vowels, consonants, stress, onsetp, codap, constraints) = (
                        list(stats.vowels), list(stats.consonants), stats.stress, stats.onsetp, stats.codap, stats.constraints)
                else:
                    (vowels, consonants) = language.phonemes.phonemes()
                    (stress, onsetp, codap, constraints) = (round(random.gauss(-0.5, 1)), random.gauss(0.5, 0.1), random.gauss(0.5, 0.1), None)
                words = list(language.lexicon.lexicon(vowels, consonants, stress, onsetp, codap, constraints, len(concept_indices), existing))
                random.shuffle(words)
                for i in range(len(concept_indices)):
                    (concept, coined) = (conceptlist[concept_indices[i]], words[i])
                    concept_words[concept] = coined
                    existing.add(coined)
        if t in loans:
            timing.start('{}borrowing words'.format(indent))
            if stats is None:
                stats = language.stats.Language(concept_words.values())
            for src in sorted(loans[t].keys()):
                concepts = {conceptlist[i] for i in loans[t][src] if conceptlist[i] in borrowsubset}
                if not concepts:
                    continue
                timing.start('{}reifying language {}'.format(indent, src))
                src_dict = reify(langs, src, t+1, concepts, timing, indent + ' ')
                for concept in concepts:
                    borrowed = borrow(src_dict.describe(*concept), stats, existing)
                    concept_words[concept] = borrowed
                    existing.add(borrowed)

    timing.start('{}building dictionary'.format(indent))
    dictionary = language.dictionary.Dictionary()
    for ((kind, index), word) in concept_words.items():
        dictionary.add(word, kind, index)
    return dictionary

class History(object):
    def __init__(self, timing, concepts):
        self._timing = timing
        self._concepts = []
        self._lookup = {}
        self._loans = {}
        self._neologisms = {}
        self._changes = [[]]
        self.coin(concepts)

    def clone(self):
        clone = History(self._timing, [])
        clone._concepts = list(self._concepts)
        clone._lookup = dict(self._lookup)
        clone._loans = dict(self._loans)
        clone._neologisms = dict(self._neologisms)
        clone._changes = [list(changes) for changes in self._changes]
        return clone

    @staticmethod
    def _nextstate():
        state = random.getstate()
        random.random()
        return state

    def _add(self, concept):
        if concept in self._lookup:
            raise KeyError('{} {} already defined'.format(*concept))
        index = len(self._concepts)
        self._concepts.append(concept)
        self._lookup[concept] = index
        return index

    def __len__(self):
        return len(self._concepts)

    def changesounds(self):
        self._changes.append([random.choice(range(len(languagesimulation.soundchanges))) for _ in self._concepts])

    def describes(self, kind, index):
        return (kind, index) in self._lookup

    def borrow(self, kind, index, src):
        t = len(self._changes) - 1
        if t not in self._loans:
            self._loans[t] = {}
        if src not in self._loans[t]:
            self._loans[t][src] = []
        concept = (kind, index)
        self._loans[t][src].append(self._add(concept))

    def coin(self, concepts):
        t = len(self._changes) - 1
        if t not in self._neologisms:
            self._neologisms[t] = []
        self._neologisms[t].append((self._nextstate(), [self._add(concept) for concept in concepts]))

    def reify(self, langs):
        timing = self._timing.routine('reifying language {}'.format(langs.index(self)))
        state = random.getstate()
        dictionary = reify(langs, langs.index(self), len(self._changes), set(self._concepts), timing, '')
        random.setstate(state)
        timing.done()
        return dictionary
