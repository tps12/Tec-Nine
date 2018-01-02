from . import phonemes
from .words import Syllable

class Constraints(object):
    def __init__(self, onsets, codae):
        self.onsets = onsets
        self.codae = codae

def constraints(lexicon):
    onsets, codae = set(), set()
    for word in lexicon:
        for syllable in word.syllables:
            onsets.add(tuple(syllable.onset))
            codae.add(tuple(syllable.coda))
    return Constraints(onsets, codae)

# get best vowel for breaking up clusters
def filler(vs):
    for v in phonemes.anaptyxity:
        if v in vs:
            return v

def constrainonset(syllable, constraints, filler):
    if not syllable.onset:
        if () in constraints.onsets:
            return [syllable]
        raise NotImplementedError('Handle empty onset')

    # look at successively smaller chunks of the whole onset
    for n in range(len(syllable.onset), 0, -1):
        clusters = [syllable.onset[i:i+n] for i in range(0, len(syllable.onset), n)]
        # if every one is a valid onset, then make syllables as necessary and we're done
        if all([tuple(cluster) in constraints.onsets for cluster in clusters]):
            return [Syllable(cluster, [filler], []) for cluster in clusters[:-1]] + [Syllable(clusters[-1], syllable.nucleus, syllable.coda)]
        # otherwise, if the first one is a valid *coda*, then prepend a vowel and treat the rest as above
        if tuple(clusters[0]) in constraints.codae and all([tuple(cluster) in constraints.onsets for cluster in clusters[1:]]):
            return [Syllable([], [filler], clusters[0])] + [Syllable(cluster, [filler], []) for cluster in clusters[1:-1]] + [Syllable(clusters[-1] if len(clusters) > 1 else [], syllable.nucleus, syllable.coda)]

def constraincoda(syllable, constraints, filler):
    if not syllable.coda:
        if () in constraints.codae:
            return [syllable]
        raise NotImplementedError('Handle empty coda')

    # look at successively smaller chunks of the whole coda
    for n in range(len(syllable.coda), 0, -1):
        clusters = [syllable.coda[i:i+n] for i in range(0, len(syllable.coda), n)]
        # if every one is a valid coda, then make syllables as necessary and we're done
        if all([tuple(cluster) in constraints.codae for cluster in clusters]):
            return [Syllable(syllable.onset, syllable.nucleus, clusters[0])] + [Syllable(cluster, [filler], []) for cluster in clusters[1:]]
        # otherwise, if the last one is a valid *onset*, then append a vowel and treat the rest as above
        if tuple(clusters[-1]) in constraints.onsets and all([tuple(cluster) in constraints.codae for cluster in clusters[:-1]]):
            return [Syllable(syllable.onset, syllable.nucleus, clusters[0] if len(clusters) > 1 else [])] + [Syllable(cluster, [filler], []) for cluster in clusters[1:]] + [Syllable(clusters[-1], [filler], [])]

def constrain(syllable, constraints, filler):
    ss = constrainonset(syllable, constraints, filler)
    return ss[:-1] + constraincoda(ss[-1], constraints, filler)
