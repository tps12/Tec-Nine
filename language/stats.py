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

