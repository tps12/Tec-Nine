from .ipa import ipa
from .orthography import getconsonantglyph, getvowelglyph
from .phonemes import vowels

def write(m):
  return ''.join([getvowelglyph(p) if p in vowels else getconsonantglyph(p) for p in m.phonemes])

def pronounce(m):
  return ''.join([ipa[p] for p in m.phonemes])
