import math
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
    def __init__(self, grid, colors, parent):
        QtOpenGL.QGLWidget.__init__(self, parent)

        self.grid = grid
        self.colors = colors
        self.objects = None
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def rotate(self, angle):
        angle = self.normalizeAngle(angle * 16)
        if angle != self.yRot:
            self.yRot = angle
            self.updateGL()

    def initializeGL(self):
        self.objects = None
        self.update()
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)

    def update(self):
        if self.objects is not None:
            GL.glDeleteLists(self.objects, 1)
        self.objects = self.makeGrid(self.grid, self.colors)

    def redraw(self):
        self.updateGL()

    def paintGL(self):
        if 'glCheckFramebufferStatus' in GL.__dict__:
            if GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER) != GL.GL_FRAMEBUFFER_COMPLETE:
                return
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glLoadIdentity()
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, (1, 1, 1, 0.25))
        GL.glTranslated(0.0, 0.0, -10.0)
        GL.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        GL.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        GL.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        GL.glCallList(self.objects)

    def resizeGL(self, width, height):
        side = min(width, height)
        GL.glViewport((width - side) / 2, (height - side) / 2, side, side)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(-1.1, 1.1, 1.1, -1.1, 0, 11)
        GL.glMatrixMode(GL.GL_MODELVIEW)

    def makeGrid(self, grid, colors):
        genList = GL.glGenLists(1)
        GL.glNewList(genList, GL.GL_COMPILE)

        for t, vs in grid.faces.iteritems():
            color = [v/255.0 for v in colors[t]]
            GL.glMaterialfv(GL.GL_FRONT, GL.GL_AMBIENT, color)
            GL.glBegin(GL.GL_TRIANGLE_FAN)
            n = normal(t)
            GL.glNormal3d(*n)
            GL.glVertex3d(*t)
            for c in vs + [vs[0]]:
                GL.glVertex3d(*c)
            GL.glEnd()

        GL.glEndList()

        return genList

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle
