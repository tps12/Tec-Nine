class Culture(object):
    def __init__(self, agriculture):
        self.agriculture = bool(agriculture)

    def __eq__(self, other):
        return self.agriculture == other.agriculture
