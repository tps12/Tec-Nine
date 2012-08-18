class ClimateClassification(object):
    def __init__(self, summary, templimits):
        self.climate = [[None for x in range(len(summary[y]))]
                        for y in range(len(summary))]

        tf = lambda c: c * (templimits[1] - templimits[0]) + templimits[0]
        pf = lambda c: c * 1800.0/len(cs)

        for y in range(len(summary)):
            for x in range(len(summary[y])):                    
                h, cs = summary[y][x]

                ts = [tf(t) for (t,p) in cs]
                ps = [pf(p) for (t,p) in cs]

                thr = sum(ts)/len(cs) * 20
                byt = sorted(range(len(ts)), key=lambda i: ts[i])
                tot = sum(ps)
                inh = sum([ps[i] for i in byt[-len(byt)/2:]])
                if inh >= 0.7 * tot:
                    thr += 280
                elif inh >= 0.3 * tot:
                    thr += 140

                k = self.koeppen(ts, ps, byt, thr, tot)

                self.climate[y][x] = (h,
                                      sum(ts)/len(ts),
                                      tot/(1800.0/len(ps))/len(ps),
                                      max(0, thr)/(20 * templimits[1] + 280.0),
                                      k)

    def koeppen(self, ts, ps, byt, thr, tot):
        if tot <= thr:
            k = u'B'
            if tot <= thr/2:
                k += u'W'
            else:
                k += u'S'
        elif min(ts) >= 18:
            k = u'A'
            if all([p >= 60*len(ps) for p in ps]):
                k += u'f'
            elif any([(100 - tot/25)*len(ps) <= p < 60*len(ps)
                      for p in ps]):
                k += u'm'
            else:
                k += u'w'
        elif max(ts) > 10:
            if min(ts) >= -3:
                k = u'C'
            else:
                k = u'D'
                
            if (min([ps[i] for i in byt[-len(byt)/2:]]) <
                max([ps[i] for i in byt[:len(byt)/2]])/10.0):
                k += u'w'
            elif (min([ps[i] for i in byt[:len(byt)/2]]) <
                  min(30*len(ps),
                      max([ps[i] for i in byt[-len(byt)/2:]])/3.0)):
                k += u's'
            else:
                k += u'f'
        else:
            k = u'E'
            if max(ts) >= 0:
                k += u'T'
            else:
                k += u'F'
                
        return k
