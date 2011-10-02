from unittest import TestCase, main

from lonrange import *

class LonRangeTestCase(TestCase):
    @staticmethod
    def equal(a, b):
        return abs(a-b) < epsilon

    def test_this_meld(self):
        r1 = LonRange(-89.4325492343, 64.092738194)
        r2 = LonRange(210.795477181, 270.567450766)

        m = LonRange.meld(r1, r2)

        self.assertTrue((self.equal(m.min, r2.min) and self.equal(m.max, r2.max + (r1.max - r1.min))) or
                        (self.equal(m.min, r1.min - (r2.max - r2.min)) and self.equal(m.max, r1.max)))

if __name__ == '__main__':
    main()
