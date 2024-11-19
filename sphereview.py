import math
import numpy

from nicegui.element import Element
import color

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
    def __init__(self, faces):
        super().__init__()

        self.faces = faces
        self.on('init', self.on_init)


    def on_init(self):
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
        colors = []
        i = 0
        for t, vs in self.faces.items():
            tile_color = [0.5, 0, i/len(self.faces)]#[v/255.0 for v in color.value(t)]
            i += 1
            for _ in range(len(vs)):
              for _ in range(3):
                for c in tile_color:
                  colors.append(c)

        #self.run_method('test', vertices, normals, colors)
        print(len(vertices))
        self.run_method('test', vertices, normals, colors)#[0,1,1]*len(vertices))

    def initializeGL(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)
        GL.glEnable(GL.GL_COLOR_MATERIAL);

        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glColorMaterial(GL.GL_FRONT, GL.GL_AMBIENT)

        GL.glLoadIdentity()
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, (1, 1, 1, 0.25))

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

        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        self._vertexBuffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._vertexBuffer)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, numpy.array(vertices, dtype='float32'), GL.GL_STATIC_DRAW)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._vertexBuffer)
        GL.glVertexPointer(3, GL.GL_FLOAT, 0, None)

        GL.glEnableClientState(GL.GL_NORMAL_ARRAY)
        self._normalBuffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._normalBuffer)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, numpy.array(normals, dtype='float32'), GL.GL_STATIC_DRAW)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._normalBuffer)
        GL.glNormalPointer(GL.GL_FLOAT, 0, None)

        GL.glEnableClientState(GL.GL_COLOR_ARRAY)
        self._colorBuffer = GL.glGenBuffers(1)
        self._colorValues = numpy.zeros(len(vertices), dtype='float32')
        self._colorValues.flags.writeable = True
        self.initialized = True

    def redraw(self):
        self.updateGL()

    def paintGL(self):
        if not self.initialized:
            return
        if 'glCheckFramebufferStatus' in GL.__dict__:
            if GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER) != GL.GL_FRAMEBUFFER_COMPLETE:
                return

        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        i = 0;
        for t, vs in self.faces.items():
            color = [v/255.0 for v in self.colors[t]]
            for _ in range(len(vs)):
              for _ in range(3):
                for c in color:
                  self._colorValues[i] = c
                  i += 1
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._colorBuffer);
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self._colorValues, GL.GL_DYNAMIC_DRAW)
        GL.glColorPointer(3, GL.GL_FLOAT, 0, None)

        GL.glLoadIdentity()
        GL.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        GL.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        GL.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3 * (6 * len(self.faces) - 12))

    def resizeGL(self, width, height):
        side = min(width, height)
        GL.glViewport(int((width - side) / 2), int((height - side) / 2), side, side)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(-1.1, 1.1, 1.1, -1.1, 0, 11)
        GL.glMatrixMode(GL.GL_MODELVIEW)

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle
