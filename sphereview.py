import math
import numpy
from OpenGL import GL
from PySide import QtCore, QtOpenGL

def squared_length(v):
    return sum([vi * vi for vi in v])

def length(v):
    return math.sqrt(squared_length(v))

def normal(v):
    d = 1.0 / length(v)
    return tuple([vi * d for vi in v])

class SphereView(QtOpenGL.QGLWidget):
    def __init__(self, grid, parent):
        QtOpenGL.QGLWidget.__init__(self, parent)

        self.grid = grid
        self.objects = None
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def usecolors(self, colors):
        self.colors = colors

    def rotate(self, angle):
        angle = self.normalizeAngle(angle * 16)
        if angle != self.yRot:
            self.yRot = angle
            self.updateGL()

    def initializeGL(self):
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
        for t, vs in self.grid.faces.iteritems():
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

    def redraw(self):
        self.updateGL()

    def paintGL(self):
        if 'glCheckFramebufferStatus' in GL.__dict__:
            if GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER) != GL.GL_FRAMEBUFFER_COMPLETE:
                return

        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        i = 0;
        for t, vs in self.grid.faces.iteritems():
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
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3 * (6 * len(self.grid.faces) - 12))

    def resizeGL(self, width, height):
        side = min(width, height)
        GL.glViewport((width - side) / 2, (height - side) / 2, side, side)

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
