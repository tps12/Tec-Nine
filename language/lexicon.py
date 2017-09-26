from random import choice, random

from words import Syllable, Word

def lexicon(vs, cs, onsetp=0.9, codap=0.5, n=10000):
  lex = set()
  for _ in range(n):
    ss = []
    while True:
      onset = [choice(cs)] if random() < onsetp else []
      coda = [choice(cs)] if random() < codap else []
      ss.append(Syllable(onset, [choice(vs)], coda))
      w = Word(ss)
      if w not in lex:
        lex.add(w)
        break
  return lex
