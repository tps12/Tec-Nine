from math import sqrt

from rtree import Rtree

class SampleSpace(object):
    def __init__(self):
        self._index = Rtree()
        self._locations = []
        self._values = []

    def __setitem__(self, location, value):
        i = len(self._locations)

        self._locations.append(location)
        self._values.append(value)
        self._index.add(i, self._locations[i])

    def __getitem__(self, location):
        js = list(self._index.nearest(location, 3))
        if len(js) == 0:
            return 0

        ds = [sqrt(sum([(self._locations[j][i]-location[i])**2 for i in range(2)]))
              for j in js]

        total = sum(ds)

        return sum([self._values[js[i]] for i in range(len(js))])/len(js)
        #return sum([self._values[js[i]] * (total - ds[i])/total/len(js) for i in range(len(js))])
