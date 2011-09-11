class LonRange(object):
    def __init__(self, minlon, maxlon):
        while maxlon < minlon: maxlon += 360

        while 540 < minlon or 540 < maxlon:
            minlon -= 360
            maxlon -= 360

        while -180 > minlon or -180 > maxlon:
            minlon += 360
            maxlon += 360
        
        self.min = minlon
        self.max = maxlon

    def __str__(self):
        return ' '.join(['LonRange:', str(self.min), '-', str(self.max)])

    def contains(self, lon):
        while lon < -180: lon += 360

        if self.min <= lon <= self.max:
            return True

        lon += 360

        if self.min <= lon <= self.max:
            return True

        return False

    def overlaps(self, other):
        if self.max - self.min >= 360 or other.max - other.min >= 360:
            return True

        if ((self.min <= other.min <= self.max) or
            (self.min <= other.max <= self.max) or
            (other.min <= self.min <= other.max) or
            (other.min <= self.max <= other.max)):
            return True

        if ((self.min <= other.min + 360 <= self.max) or
            (self.min <= other.max + 360 <= self.max) or
            (other.min <= self.min + 360 <= other.max) or
            (other.min <= self.max + 360 <= other.max)):
            return True

        return False

    def meld(self, other):
        print 'melding', self, other
        if other is None:
            return True

        if self.max - self.min >= 360:
            return True

        if other.max - other.min >= 360:
            self.min = -180.0
            self.max = 180.0
            return True

        if (self.min <= other.min + 360 <= self.max or
            self.min <= other.max + 360 <= self.max):
            other.min += 360
            other.max += 360

        if (other.min <= self.min + 360 <= other.max or
            other.min <= self.max + 360 <= other.max):
            other.min -= 360
            other.max -= 360

        if ((self.min <= other.min <= self.max) or
            (self.min <= other.max <= self.max) or
            (other.min <= self.min <= other.max) or
            (other.min <= self.max <= other.max)):
            self.min = min(self.min, other.min)
            self.max = max(self.max, other.max)

            if self.max - self.min >= 360:
                self.min = -180.0
                self.max = 180.0
            return True

        import pdb; pdb.set_trace()
        return False
