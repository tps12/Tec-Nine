from random import choice, random

from . import phonemes
from .words import Syllable, Word

def wordkey(word):
  return tuple([phonemes.height(p) if p in phonemes.vowels else p for p in word.phonemes])

def lexicon(vs, cs, onsetp=0.9, codap=0.5, n=10000, seen=None):
  seen = set() if seen is None else {wordkey(w) for w in seen}
  lex = set()
  for _ in range(n):
    ss = []
    while True:
      onset = [choice(cs)] if random() < onsetp else []
      coda = [choice(cs)] if random() < codap else []
      ss.append(Syllable(onset, [choice(vs)], coda))
      w = Word(ss)
      ps = wordkey(w)
      if ps not in seen:
        seen.add(ps)
        lex.add(w)
        break
  return lex
