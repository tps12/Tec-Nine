epsilon = 1/3600.0/100 # 1/100th of a second

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

    @staticmethod
    def meld(a, b):
        amin, amax, bmin, bmax = a.min, a.max, b.min, b.max

        if amax - amin + epsilon >= 360 or bmax - bmin + epsilon >= 360:
            return LonRange(-180, 180)

        if (amin - epsilon <= bmin + 360 <= amax + epsilon or
            amin - epsilon <= bmax + 360 <= amax + epsilon or
            bmin - epsilon <= amin - 360 <= bmax + epsilon or
            bmin - epsilon <= amax - 360 <= bmax + epsilon):
            bmin += 360
            bmax += 360

        if (bmin - epsilon <= amin + 360 <= bmax + epsilon or
            bmin - epsilon <= amax + 360 <= bmax + epsilon or
            amin - epsilon <= bmin - 360 <= amax + epsilon or
            amin - epsilon <= bmax - 360 <= amax + epsilon):
            bmin -= 360
            bmax -= 360

        if ((amin - epsilon <= bmin <= amax + epsilon) or
            (amin - epsilon <= bmax <= amax + epsilon) or
            (bmin - epsilon <= amin <= bmax + epsilon) or
            (bmin - epsilon <= amax <= bmax + epsilon)):
            amin = min(amin, bmin)
            amax = max(amax, bmax)

            if amax - amin >= 360:
                amin = -180.0
                amax = 180.0
            return LonRange(amin, amax)

        import pdb; pdb.set_trace()
        return None
