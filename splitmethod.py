def split(tiles):
    a = [0, 0, 0]
    for tile in tiles:
        for i in range(len(a)):
            a[i] += tile.vector[i]
    a = [float(c)/len(tiles) for c in a]
    c, cd2 = None, float('inf')
    for tile in tiles:
        d2 = sum([(tile.vector[i]-a[i])**2 for i in range(len(a))])
        if d2 < cd2:
            c = tile
            cd2 = d2
    c.value = 2
