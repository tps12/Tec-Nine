import math

from nicegui.element import Element

def squared_length(v):
    return sum([vi * vi for vi in v])

def length(v):
    return math.sqrt(squared_length(v))

def normal(v):
    d = 1.0 / length(v)
    return tuple([vi * d for vi in v])

def rotate_axes(x, y, z):
    return (-y, z, x)

class SphereView(Element, component='sphereview.js'):
    def __init__(self, faces, on_click=None):
        super().__init__()

        self.faces = faces
        self.colors = { v: (128, 128, 128) for v in self.faces }
        self.on_click = on_click
        self.on('mounted', self.initialize)
        self.on('clicked', self.click)

    def click(self, event):
        if self.on_click:
            self.on_click(*event.args)

    def usecolors(self, colors):
        self.colors = colors
        self.update_colors()

    def update_colors(self):
        colors = []
        for t, vs in self.faces.items():
            color = [v/255 for v in self.colors[t]]
            for _ in range(len(vs)):
              for _ in range(3):
                for c in color:
                  colors.append(c)
        self.run_method('setColors', colors)

    def rotate(self, value):
        self.run_method('rotate', value * math.pi/180)

    def initialize(self):
        vertices = []
        normals = []
        for t, vs in self.faces.items():
            t = rotate_axes(*t)
            vs = [rotate_axes(*v) for v in vs]
            n = normal(t)
            for i in range(len(vs)):
                vertices += t
                vertices += vs[i-1]
                vertices += vs[i]
                normals += 3 * n
        self.run_method('initialize', vertices, normals)
        self.update_colors()

