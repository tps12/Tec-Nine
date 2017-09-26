vglyphs = dict([
    ('&', 'a'),
    ('V"', 'u'),
    ('V', 'u'),
    ('@', 'e')])

def getvowelglyph(v):
    global vglyphs

    if v in vglyphs:
        return vglyphs[v]
    return v[0].lower()

cglyphs = dict([
    ('P', 'f'),
    ('B', 'b'),
    ('T', 'th'),
    ('D', 'th'),
    ('*', 'r'),
    ('*.', 'r'),
    ('S', 'sh'),
    ('Z', 'zh'),
    ('c', 'k'),
    ('C', 'hy'),
    ('j', 'y'),
    ('l^', 'ly'),
    ('N', 'ng'),
    ('Q', 'g'),
    ('G', 'q'),
    ('x', 'ch'),
    ('X', 'ch'),
    ('g"', 'r'),
    ('?', "'")])

def getconsonantglyph(c):
    global cglyphs

    if c in cglyphs:
        return cglyphs[c]
    return c[0].lower()
