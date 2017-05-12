class set(object):
  def __init__(self):
    self.parent = self
    self.rank = 0

  def root(self):
    if self.parent != self:
      self.parent = self.parent.root()
    return self.parent

def union(x, y):
  xr = x.root()
  yr = y.root()
  if xr == yr:
    return
  if xr < yr:
    xr.parent = yr
  else:
    yr.parent = xr
    if xr > yr:
      xr.rank += 1
