def transform(layers):
    # accumulate depth from top down
    t = 0
    for i in range(len(layers)-1, -1, -1):
        t += layers[i]['thickness']
        dt = t - 5
        # beneath 5km, everything metamorphoses
        if dt >= 0:
            # metamorphosed layers
            newlayers = [{ 'rock': dict(l['rock']), 'thickness': l['thickness'] } for l in layers[:i]]
            # deep part of divided layer
            newlayers.append({ 'rock': layers[i]['rock'], 'thickness': dt })
            # metamorphose
            for l in newlayers:
                l['rock']['type'] = 'M'
                l['rock']['name'] = 'M'
            # remaining piece of divided layer
            newlayers.append({ 'rock': layers[i]['rock'], 'thickness': layers[i]['thickness'] - dt })
            # un-metamorphosed layers
            newlayers += layers[i+1:]
            return newlayers
    else:
        return layers
