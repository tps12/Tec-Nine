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

    @staticmethod
    def meld(a, b):
        if a.max - a.min >= 180 or b.max - b.min >= 180:
            return LatRange(-90, 90)

        if ((a.min <= b.min <= a.max) or
            (a.min <= b.max <= a.max) or
            (b.min <= a.min <= b.max) or
            (b.min <= a.max <= b.max)):
            mmin = min(a.min, b.min)
            mmax = max(a.max, b.max)

            if mmax - mmin >= 180:
                mmin = -90.0
                mmax = 90.0
            return LatRange(mmin, mmax)

        return None
