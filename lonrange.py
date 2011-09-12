epsilon = 1/3600.0/100 # 1/100th of a second

class LonRange(object):
    def __init__(self, minlon, maxlon):
        while maxlon < minlon: maxlon += 360
        if maxlon - minlon > 180:
            temp = maxlon
            maxlon = minlon
            minlon = temp
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

        if ((self.min + epsilon <= other.min <= self.max - epsilon) or
            (self.min + epsilon <= other.max <= self.max - epsilon) or
            (other.min + epsilon <= self.min <= other.max - epsilon) or
            (other.min + epsilon <= self.max <= other.max - epsilon)):
            return True

        if ((self.min + epsilon <= other.min + 360 <= self.max - epsilon) or
            (self.min + epsilon <= other.max + 360 <= self.max - epsilon) or
            (other.min + epsilon <= self.min + 360 <= other.max - epsilon) or
            (other.min + epsilon <= self.max + 360 <= other.max - epsilon)):
            return True

        return False

    def meld(self, other):
        if other is None:
            return True

        if self.max - self.min + epsilon >= 360:
            return True

        if other.max - other.min + epsilon >= 360:
            self.min = -180.0
            self.max = 180.0
            return True

        if (self.min - epsilon <= other.min + 360 <= self.max + epsilon or
            self.min - epsilon <= other.max + 360 <= self.max + epsilon or
            other.min - epsilon <= self.min - 360 <= other.max + epsilon or
            other.min - epsilon <= self.max - 360 <= other.max + epsilon):
            other.min += 360
            other.max += 360

        if (other.min - epsilon <= self.min + 360 <= other.max + epsilon or
            other.min - epsilon <= self.max + 360 <= other.max + epsilon or
            self.min - epsilon <= other.min - 360 <= self.max + epsilon or
            self.min - epsilon <= other.max - 360 <= self.max + epsilon):
            other.min -= 360
            other.max -= 360

        if ((self.min - epsilon <= other.min <= self.max + epsilon) or
            (self.min - epsilon <= other.max <= self.max + epsilon) or
            (other.min - epsilon <= self.min <= other.max + epsilon) or
            (other.min - epsilon <= self.max <= other.max + epsilon)):
            self.min = min(self.min, other.min)
            self.max = max(self.max, other.max)

            if self.max - self.min >= 360:
                self.min = -180.0
                self.max = 180.0
            return True

        import pdb; pdb.set_trace()
        return False
