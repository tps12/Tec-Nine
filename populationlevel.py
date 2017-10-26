def paleolithic(k):
  if k[0] == u'A':
    return 35
  return 5

def withagriculture(k):
  if k[0] in u'AC':
    return 150
  if k[0] == u'D':
    return 100
  return 50

def count(tile, race, agricultural):
  return (withagriculture if race in agricultural else paleolithic)(tile.climate.koeppen)
