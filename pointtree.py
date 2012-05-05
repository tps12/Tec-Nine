class PointTree(object):
    def __init__(self, *vs):
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
        return [n[1][0] for n in ns] if len(ns[0][1]) == 1 else [tuple(n[1]) for n in ns]

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
            return sum([(1 if v[i] > self._medians[i] else 0) << i for i in range(len(v))])

        def depth(self):
            return 1 + max([c.depth() for c in self._children])

        def contents(self):
            return [cc for c in self._children for cc in c.contents()]

        def nearest(self, v, k, ns = None):
            ci = self._child(v)
            ns = sorted((ns or []) + self._children[ci].nearest(v, k), key=lambda n: n[0])[0:k]
            for c in range(len(v)):
                vm = list(v)
                vm[c] = self._medians[c]
                if len(ns) < k or PointTree.d2(v, vm) < ns[-1][0]:
                    cmi = self._child(vm)
                    if cmi == ci: continue
                    ns = self._children[cmi].nearest(v, k, ns)
            return ns

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
