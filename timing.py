from time import time

class Timing(object):
    def routine(self, name):
        return self.Routine(name)

    class Routine(object):
        def __init__(self, name):
            self._start = time()

            print name
            print '-' * len(name)

            self._t, self._current = None, None

        def _record(self):
            t = time()
            if self._current is not None:
                print self._current, t - self._t
            self._t = t

        def start(self, section):
            self._record()
            self._current = section

        def done(self):
            self._record()
            print 'total', time() - self._start
            print
