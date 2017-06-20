class Heritage(object):
  last = [0]
  def __init__(self, ancestry=None):
    if ancestry is None:
      self.last[0] = 0
    self.serial = self.last[0]
    self.last[0] += 1
    self.ancestry = ancestry
