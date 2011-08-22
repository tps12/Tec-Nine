class LatRange(object):
    def __init__(self, minlat, maxlat):
        self.min = minlat
        self.max = maxlat

    def overlaps(self, other):
        if self.max - self.min >= 180 or other.max - other.min >= 180:
            return True

        if ((self.min <= other.min <= self.max) or
            (self.min <= other.max <= self.max) or
            (other.min <= self.min <= other.max) or
            (other.min <= self.max <= other.max)):
            return True
        return False

    def meld(self, other):
        if other is None:
            return True

        if self.max - self.min >= 180:
            return True

        if other.max - other.min >= 180:
            self.min = -90.0
            self.max = 90.0
            return True

        if ((self.min <= other.min <= self.max) or
            (self.min <= other.max <= self.max) or
            (other.min <= self.min <= other.max) or
            (other.min <= self.max <= other.max)):
            self.min = min(self.min, other.min)
            self.max = max(self.max, other.max)

            if self.max - self.min >= 180:
                self.min = -90.0
                self.max = 90.0
            return True

        return False
