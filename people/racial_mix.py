class RaceContribution(object):
    def __init__(self, fraction, heritage):
        self.fraction = float(fraction)
        self.heritage = heritage

    def __eq__(self, other):
        return abs(self.fraction - other.fraction) < 0.01 and self.heritage == other.heritage

class RacialMix(object):
    def __init__(self, contributions):
        self.contributions = list(contributions)

    def __eq__(self, other):
        by_heritage_name = lambda c: c.heritage.name
        return sorted(self.contributions, key=by_heritage_name) == sorted(other.contributions, key=by_heritage_name)
