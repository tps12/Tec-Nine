from .ipa import ipa
from .orthography import getconsonantglyph, getvowelglyph
from .phonemes import vowels

def write(m):
  return ''.join([getvowelglyph(p) if p in vowels else getconsonantglyph(p) for p in m.phonemes])

def pronounce(m):
  p = ''
  for i in range(len(m.syllables)):
    if i == m.stress:
      p += '\u02c8'
    p += ''.join([ipa[p] for p in m.syllables[i].phonemes])
  return p
