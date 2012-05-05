class PointTree(object):
    def __init__(self, *vs):
        if len(vs) == 1:
            try:
                self._values = dict(vs[0])
                vs = vs[0].keys()
            except TypeError:
                raise ValueError('Must specify at least two points')
        else:
            if len(set(vs)) < len(vs):
                raise ValueError('Points must be unique')
            self._values = dict([[v, v] for v in vs])
        if len(vs) < 2: raise ValueError('Must specify at least two points')
        try: iter(vs[0])
        except TypeError: vs = [[v] for v in vs]
        self._dimension = len(vs[0])
        if any([len(v) != self._dimension for v in vs[1:]]):
            raise ValueError('Points must have uniform number of dimensions')
        
        self._root = self.branch([[float(c) for c in v] for v in vs])

    def depth(self):
        return self._root.depth()

    def nearest(self, v, k = 1):
        try: iter(v)
        except TypeError: v = [v]
        ns = self._root.nearest(v, k)
        keys = [n[1][0] for n in ns] if len(ns[0][1]) == 1 else [tuple(n[1]) for n in ns]
        return [self._values[k] for k in keys]

    @classmethod
    def branch(cls, vs):
        if len(vs) == 0 or len(vs) < 2**(len(vs[0])+1):
            t = cls._Leaf(vs)
        else:
            try:
                t = cls._Branch(vs)
            except ValueError:
                t = cls._Leaf(vs)
        return t

    @staticmethod
    def d2(v1, v2):
        return sum([(v1[c]-v2[c])*(v1[c]-v2[c]) for c in range(len(v1))])

    class _Branch(object):
        def __init__(self, vs):
            ranges = [[float('inf'), float('-inf')] for c in range(len(vs[0]))]
            for v in vs:
                for c in range(len(v)):
                    if v[c] < ranges[c][0]: ranges[c][0] = v[c]
                    if v[c] > ranges[c][1]: ranges[c][1] = v[c]
            self._medians = [(ranges[c][1] - ranges[c][0])/2 for c in range(len(vs[0]))]
            cvss = [[] for i in range(2**len(vs[0]))]
            for v in vs:
                cvss[self._child(v)].append(v)
            if any([len(cvs) == len(vs) for cvs in cvss]):
                raise ValueError
            self._children = [PointTree.branch(cvs) for cvs in cvss]

        def _child(self, v):
            # index of the child containing v
            # each dimension gets a bit: 1 if it's greater than the median, else 0
            return sum([(1 if v[i] > self._medians[i] else 0) << i for i in range(len(v))])

        def depth(self):
            return 1 + max([c.depth() for c in self._children])

        def contents(self):
            return [cc for c in self._children for cc in c.contents()]

        def nearest(self, v, k, ns = None):
            ns = [] if ns is None else ns
            for (ci, p) in self._nearestbounds(v):
                if len(ns) < k or PointTree.d2(v, p) < ns[-1][0]:
                    ns = sorted(ns + self._children[ci].nearest(v, k), key=lambda n: n[0])[0:k]
            return ns

        def _nearestbounds(self, v):
            """Get child index and nearest point tuples in which to look for points close to v.

            The first item is always a tuple of the child index containing v and v itself.
            Subsequent items consist of the index of another branch and a point representing the
            nearest possible location to v in that branch.
            """
            ci = self._child(v)
            bs = [(ci, v)] # always start with v's own branch
            for bi in range(len(self._children)):
                if bi == ci: continue
                diff = bi ^ ci
                bits = [diff & (1 << i) == (1 << i) for i in range(len(v))]
                p = [self._medians[i] if bits[i] else v[i] for i in range(len(bits))]
                bs.append((bi, p))
            return bs

        def __repr__(self):
            return 'PointTree._Branch({0})'.format(repr([tuple(v) for v in self.contents()]))

    class _Leaf(object):
        def __init__(self, vs):
            self._vs = vs

        def contents(self):
            return self._vs

        def depth(self):
            return 0

        def nearest(self, v, k, ns = None):
            ns = ns if ns is not None else []
            for tv in self._vs:
                d2 = PointTree.d2(v, tv)
                if len(ns) == 0 or len(ns) < k or d2 < ns[-1][0]:
                    ns = sorted(ns + [(d2,tv)], key=lambda n: n[0])[0:k]
            return ns

        def __repr__(self):
            return 'PointTree._Leaf({0})'.format(repr([tuple(v) for v in self.contents()]))
