def dist2(p1, p2):
    """Get the distance squared between two points."""
    return sum([(p1[i]-p2[i])**2 for i in range(len(p1))])
