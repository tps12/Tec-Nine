class Heritage(object):
  def __init__(self, name, ancestry=None):
    self.name = name
    self.ancestry = ancestry

  def __eq__(self, other):
    return self.name == other.name

  def __hash__(self):
    return hash(self.name)
