import people.racial_mix
import vector

# major languages spoken by strictly greater than 25% of the population
major_language_threshold = 0.25

class Community(object):
    def __init__(self, thousands, nationality, racial_mix, language, culture):
        self.thousands = float(thousands)
        self.nationality = int(nationality)
        self.racial_mix = racial_mix
        self.language = int(language)
        self.culture = culture

def intermingle(communities):
    # each race is a dimension, each mix is a vector
    pops, mixes = [], []
    for community in communities:
        pops.append(community.thousands)
        mixes.append(community.racial_mix)
    dimensions = sorted(
        {c.heritage for mix in mixes for c in mix.contributions if c.fraction > 0},
        key=lambda h: h.name)
    totals = []
    for mix_index in range(len(mixes)):
        mix = mixes[mix_index]
        total = [0 for _ in dimensions]
        for c in mix.contributions:
            for i in range(len(dimensions)):
                if c.heritage == dimensions[i]:
                    total[i] = c.fraction
                    break
        totals.append(total)

    # find the average of all communities, weighted by population
    centroid = vector.centroid(totals, pops)

    # differences to the mean from each mix
    diffs = [vector.diff(centroid, total) for total in totals]

    # the smallest community changes the most, up to 2 percentage points
    # everything else scaled to that
    smallest_index = min(range(len(pops)), key=lambda i: pops[i])
    scaled = [vector.scalemax(diffs[i], .02 * pops[smallest_index]/pops[i]) for i in range(len(pops))]
    new_mixes = [vector.add(totals[i], scaled[i]) for i in range(len(pops))]

    return [Community(communities[i].thousands, communities[i].nationality, 
                      people.racial_mix.RacialMix(
                          [people.racial_mix.RaceContribution(new_mixes[i][j], dimensions[j])
                           for j in range(len(dimensions)) if new_mixes[i][j] > 0]),
                      communities[i].language, communities[i].culture)
            for i in range(len(communities))]

def assimilate(communities):
    langpops = {}
    for c in communities:
        if c.language not in langpops:
            langpops[c.language] = 0
        langpops[c.language] += c.thousands
    total = sum(langpops.values())
    thresh = total * major_language_threshold
    maj = sorted([lang for (lang, pop) in langpops.items() if pop > thresh])
    if not maj:
        return communities
    majtotal = sum([langpops[lang] for lang in maj])
    majprops = {lang: langpops[lang]/majtotal for lang in maj}
    langthresh = total * 0.01
    output = []
    for c in communities:
        if c.thousands < 1 and langpops[c.language] < langthresh:
            output += [Community(c.thousands * majprops[lang], c.nationality, c.racial_mix, lang, c.culture)
                       for lang in maj]
        else:
            output.append(c)
    return output
