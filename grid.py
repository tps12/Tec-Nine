from functools import reduce
import math

def squared_length(v):
    return sum([vi * vi for vi in v])

def length(v):
    return math.sqrt(squared_length(v))

def normal(v):
    d = 1.0 / length(v)
    return tuple([vi * d for vi in v])

def cross(v1, v2):
    return (
        v1[1]*v2[2] - v1[2]*v2[1],
        v1[2]*v2[0] - v1[0]*v2[2],
        v1[0]*v2[1] - v1[1]*v2[0])

def dot(v1, v2):
    return sum([v1[i] * v2[i] for i in range(3)])

# A spherical "grid" divided into hex/pentagons
#
# A size 0 grid is a dodecahedron, and each subsequent size is the result
# of taking the previous size and subdividing the previous size's vertices
# into faces.
#
# Therefore, the number of faces for a given sized grid is:
#
# >>> def f(i):
# ...     return 12 if i == 0 else f(i-1) + v(f(i-1))
#
# where
#
# >>> def v(f):
# ...     p = 12 # number of pentagons is fixed at 12
# ...     h = f - p # everything else is a hexagon
# ...     return p * 5/3 + h * 2
#
# A rectangular grid with approximate size of 2 degrees on a side provides
# 10,316 tiles, a little more than the 7,292 provided by a size 6 hex grid
# and well below the 21,872 provided by a size 7.
#
# An earth-sized sphere divided into a grid of size 29
# (686,303,773,648,832 tiles!) provides an average tile size of
# 0.743 m^2 and around a linear meter between adjacent tiles.
#
# The grid consists of two dictionaries, one mapping faces to each face's
# 5- or 6-length vertex list, and the other mapping vertices to each vertex's
# set of adjacent faces (3 of them if the faces are all defined at that size).
# All locations are vectors on the unit sphere.
class Grid(object):
    def __init__(self, prev=None):
        self.prev = prev
        self.size = self.prev.size + 1 if self.prev is not None else 0
        self.faces = {}
        self.vertices = {}

        if self.prev is None:
            x = -0.525731112119133606
            z = -0.850650808352039932

            dodecfaces = [
                    (-x, 0, z), (x, 0, z), (-x, 0, -z), (x, 0, -z),
                    (0, z, x), (0, z, -x), (0, -z, x), (0, -z, -x),
                    (z, x, 0), (-z, x, 0), (z, -x, 0), (-z, -x, 0)
            ]

            dodecneighbors = [
                    (9, 4, 1, 6, 11), (4, 8, 10, 6, 0), (11, 7, 3, 5, 9), (2, 7, 10, 8, 5),
                    (9, 5, 8, 1, 0), (2, 3, 8, 4, 9), (0, 1, 10, 7, 11), (11, 6, 10, 3, 2),
                    (5, 3, 10, 1, 4), (2, 5, 4, 0, 11), (3, 7, 6, 1, 8), (7, 2, 9, 0, 6)
            ]

            for i in range(len(dodecfaces)):
                self._makeface(
                    dodecfaces[i],
                    [dodecfaces[n] for n in reversed(dodecneighbors[i])])

    def _addface(self, face):
        for vertex in self.faces[face]:
            if vertex not in self.vertices:
                self.vertices[vertex] = vertexfaces = set()
            else:
                vertexfaces = self.vertices[vertex]
            if face not in vertexfaces:
                vertexfaces.add(face)

    def _makeface(self, newface, neighbors):
        vertices = []
        for n1, n2 in zip(neighbors, [neighbors[-1]] + neighbors):
            # sort for floating-point consistency
            faces = sorted((newface, n1, n2))
            vertices.append(
                normal([sum([face[i] for face in faces]) for i in range(3)]))
        self.faces[newface] = vertices
        self._addface(newface)

    # Populates grid by subdividing a single tile from the previous size
    #
    # If face is omitted, full previous size is subdivided
    def populate(self, previousface=None):
        if previousface is None:
            for f in self.prev.faces:
                self.populate(f)
            return

        if previousface in self.faces:
            return

        if previousface not in self.prev.faces:
            self.prev.populate(previousface)

        for vertex in self.prev.faces[previousface]:
            if len(self.prev.vertices[vertex]) < 3:
                # implies p was new in prev
                # i.e., p was a vertex in prev's prev
                # implies p in prev prev had three faces
                for neighbor in self.prev.prev.vertices[previousface]:
                    self.prev.populate(neighbor)

        # face from face
        self._makeface(previousface, self.prev.faces[previousface])

        # faces from vertices
        for vertex in self.prev.faces[previousface]:
            vertices = []
            faces = list(self.prev.vertices[vertex])
            # for each pair of faces meeting at the previous vertex
            for f1, f2 in zip(faces, faces[1:] + faces[0:1]):
                commonvertices = list(
                    set(self.prev.faces[f1]) & set(self.prev.faces[f2]))
                # new vertex at the midpoint between the two common old vertices and old face location
                for neighbor in f1, f2:
                    # sort for floating-point consistency
                    faces = sorted([neighbor] + commonvertices)
                    vertices.append(
                        normal([sum([face[i] for face in faces]) for i in range(3)]))
            # make sure new vertices wind correctly
            if dot(vertex, cross(*vertices[0:2])) > 0:
                vertices = list(reversed(vertices))
            self.faces[vertex] = vertices
            self._addface(vertex)

    def edges(self, face):
        vertices = self.faces[face]
        return [tuple(sorted(vs)) for vs in zip(vertices, vertices[1:] + vertices[0:1])]

    def borders(self, face, edge):
        edges = self.edges(face)
        source = edges.index(edge)
        return edges[source + 1:] + edges[:source]

    def neighbor(self, face, border):
        # each edge has two common faces (if they exist in the grid)
        common = self.vertices[border[0]] & self.vertices[border[1]]
        if len(common) == 2:
            return list(common - { face })[0]

    def neighbors(self, face):
        return reduce(
            lambda a, b: a.union(b),
            [self.vertices[v] for v in self.faces[face]],
            set()).difference(set((face,)))

    # get the radian distance between adjacent faces
    # neighboring hexes are used for grid sizes > 0
    def scale(self):
        found = False
        for f, vs in self.faces.items():
            if len(vs) == 6:
                for n in [self.neighbor(f, e) for e in self.edges(f)]:
                    if n in self.faces and len(self.faces[n]) == 6:
                        found = True
                        break
                if found:
                    break
        else:
            f = list(self.faces.keys())[0]
            n = self.neighbor(f, self.edges(f)[0])
        return abs(math.acos(dot(f, n)))
