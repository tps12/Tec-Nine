class LatRange(object):
    def __init__(self, lat1, lat2):
        self.min = min(lat1, lat2)
        self.max = max(lat1, lat2)

    def __str__(self):
        return ' '.join(['LatRange:', str(self.min), '-', str(self.max)])

    def contains(self, lat):
        return self.min <= lat <= self.max

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
