def popstr(thousands):
  if thousands >= 10:
    value = round(thousands) * 1000
  elif thousands >= 1:
    value = round(thousands * 10) * 100
  elif thousands >= 0.1:
    value = round(thousands * 100) * 10
  else:
    value = round(thousands * 1000)
  return u'{:,}'.format(value)

def percent(fraction):
  if fraction == 0:
    value = 0
  else:
    value = round(fraction * 100)
    if value == 0:
      value = '<1'
    elif value == 100 and fraction < 1:
      value = '>99'
  return u'{}%'.format(value)

def percents(values):
  target, total = sum(values), 0
  for value in values:
    value = (value if total < 1 else 0.0000001)/target
    total += value
    yield percent(value)
