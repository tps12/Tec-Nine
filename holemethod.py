def findholes(tiles, group, adj, index):
    # contiguous chunks of tile that are adjacent to the new shape but not included in it
    # these may be outside the shape's boundary, or they may be "holes" that need filling in
    holegroups = []
    for t in group:
        for ta in adj[t]:
            if ta not in group and not any([ta in g for g in holegroups]):
                for aa in [aa for aa in adj[ta] if aa not in group]:
                    for g in holegroups:
                        if aa in g:
                            g.add(ta)
                            break
                    else:
                        holegroups.append(set([ta]))

    for i in range(3):
        for g in holegroups:
            for t in list(g):
                for ta in adj[t]:
                    if ta not in group and not any([ta in og for og in holegroups]):
                        g.add(ta)

    boundaries = []
    testgroups = list(holegroups)
    for g in testgroups:
        for t in g:
            removed = False
            for ta in adj[t]:
                if ta not in group and not any([ta in og for og in testgroups]):
                    boundaries.append(g)
                    removed = True
                    break
            if removed:
                break

    return [t for g in holegroups for t in g], [t for g in boundaries for t in g]
