import moderngl
from PyQt5 import QtOpenGL, QtWidgets, QtCore
import numpy as np
import openmesh as om
from pyrr import Matrix44

from ArcBall import ArcBallUtil


class QGLControllerWidget(QtOpenGL.QGLWidget):

    def __init__(self, parent=None):
        self.parent = parent
        super(QGLControllerWidget, self).__init__(parent)
        

    def initializeGL(self):
        
        self.ctx = moderngl.create_context()

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330
                uniform mat4 Mvp;
                in vec3 in_position;
                in vec3 in_normal;
                out vec3 v_vert;
                out vec3 v_norm;
                void main() {
                    v_vert = in_position;
                    v_norm = in_normal;
                    gl_Position = Mvp * vec4(in_position, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                uniform vec4 Color;
                uniform vec3 Light;
                in vec3 v_vert;
                in vec3 v_norm;
                out vec4 f_color;
                void main() {
                    float lum = dot(normalize(v_norm),
                                    normalize(v_vert - Light));
                    lum = acos(lum) / 3.14159265;
                    lum = clamp(lum, 0.0, 1.0);
                    lum = lum * lum;
                    lum = smoothstep(0.0, 1.0, lum);
                    lum *= smoothstep(0.0, 80.0, v_vert.z) * 0.3 + 0.7;
                    lum = lum * 0.8 + 0.2;
                    vec3 color = Color.rgb * Color.a;
                    f_color = vec4(color * lum, 1.0);
                }
            '''
        )

        self.light = self.prog['Light']
        self.color = self.prog['Color']
        self.mvp = self.prog['Mvp']
        self.mesh = None
        width = max(self.width(), 2)
        height = max(self.height(), 2)
        self.arc_ball = ArcBallUtil(width, height)
        # self.arc_ball = ArcBallUtil(self.width(), self.height())
        self.center = np.zeros(3)
        self.scale = 1.0
    def create_grid(self, size=10, step=1):
        """Creates a grid in the X-Y plane centered at the origin."""
        lines = []
        for i in range(-size, size + 1, step):
            # Lines parallel to Y axis
            lines.append([i, -size, 0])
            lines.append([i, size, 0])
            # Lines parallel to X axis
            lines.append([-size, i, 0])
            lines.append([size, i, 0])
        grid_vertices = np.array(lines, dtype='f4')
        self.grid_vbo = self.ctx.buffer(grid_vertices.tobytes())
        self.grid_vao = self.ctx.simple_vertex_array(
            self.prog, self.grid_vbo, 'in_position'
        )
        self.grid_vertex_count = len(grid_vertices)

    
    def set_mesh(self, mesh):
        self.mesh = mesh
        self.mesh.update_normals()
        assert(self.mesh.n_vertices() > 0 and self.mesh.n_faces() > 0)
        index_buffer = self.ctx.buffer(
            np.array(self.mesh.face_vertex_indices(), dtype="u4").tobytes())
        vao_content = [
            (self.ctx.buffer(
                np.array(self.mesh.points(), dtype="f4").tobytes()),
                '3f', 'in_position'),
            (self.ctx.buffer(
                np.array(self.mesh.vertex_normals(), dtype="f4").tobytes()),
                '3f', 'in_normal')
        ]
        self.vao = self.ctx.vertex_array(
                self.prog, vao_content, index_buffer, 4,
            )
        self.init_arcball()

    def init_arcball(self):
        width = max(self.width(), 2)
        height = max(self.height(), 2)
        self.arc_ball = ArcBallUtil(width, height)
        # self.arc_ball = ArcBallUtil(self.width(), self.height())
        pts = self.mesh.points()
        bbmin = np.min(pts, axis=0)
        bbmax = np.max(pts, axis=0)
        self.center = 0.5*(bbmax+bbmin)
        self.scale = np.linalg.norm(bbmax-self.center)
        self.arc_ball.Transform[:3, :3] /= self.scale
        self.arc_ball.Transform[3, :3] = -self.center/self.scale
    def paintGL(self):
        self.ctx.clear(1.0, 1.0, 1.0)
        self.ctx.enable(moderngl.DEPTH_TEST)

        self.aspect_ratio = self.width()/max(1.0, self.height())
        proj = Matrix44.perspective_projection(60.0, self.aspect_ratio,
                                               0.1, 1000.0)
        lookat = Matrix44.look_at(
            (0.0, 0.0, 2.0),  # eye
            (0.0, 0.0, 0.0),  # target
            (0.0, 1.0, 0.0),  # up
        )

        self.light.value = (1.0, 1.0, 1.0)
        self.color.value = (0.7, 0.7, 0.7, 0.5)
        self.arc_ball.Transform[3, :3] = \
            -self.arc_ball.Transform[:3, :3].T@self.center
        self.mvp.write(
            (proj * lookat * self.arc_ball.Transform).astype('f4'))

        # Draw grid if available
        if hasattr(self, 'grid_vao'):
            self.grid_vao.render(mode=moderngl.LINES, vertices=self.grid_vertex_count)

        # Draw mesh if available
        if self.mesh is not None:
            self.color.value = (1.0, 1.0, 1.0, 0.8)
            self.vao.render()
    # def paintGL(self):
    #     self.ctx.clear(1.0, 1.0, 1.0)
    #     self.ctx.enable(moderngl.DEPTH_TEST)

    #     if self.mesh is None:
    #         return

    #     self.aspect_ratio = self.width()/max(1.0, self.height())
    #     proj = Matrix44.perspective_projection(60.0, self.aspect_ratio,
    #                                            0.1, 1000.0)
    #     lookat = Matrix44.look_at(
    #         (0.0, 0.0, 2.0),  # eye
    #         (0.0, 0.0, 0.0),  # target
    #         (0.0, 1.0, 0.0),  # up
    #     )

    #     self.light.value = (1.0, 1.0, 1.0)
    #     self.color.value = (1.0, 1.0, 1.0, 0.8)
    #     self.arc_ball.Transform[3, :3] = \
    #         -self.arc_ball.Transform[:3, :3].T@self.center
    #     self.mvp.write(
    #         (proj * lookat * self.arc_ball.Transform).astype('f4'))

    #     self.vao.render()

    def resizeGL(self, width, height):
        width = max(2, width)
        height = max(2, height)
        self.ctx.viewport = (0, 0, width, height)
        self.arc_ball.setBounds(width, height)
        return

    def mousePressEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self.arc_ball.onClickLeftDown(event.x(), event.y())

    def mouseReleaseEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self.arc_ball.onClickLeftUp()

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self.arc_ball.onDrag(event.x(), event.y())
    def wheelEvent(self, event):
        # Zoom in/out with mouse wheel
        
        if event.type() == QtCore.QEvent.Wheel:
            delta = event.angleDelta().y()
            self.arc_ball.onScroll(delta)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.resize(640, 480)
        self.setWindowTitle('Mesh Viewer')
        self.gl = QGLControllerWidget(self)

        self.setCentralWidget(self.gl)
        self.menu = self.menuBar().addMenu("&File")
        self.menu.addAction('&Open', self.openFile)

        timer = QtCore.QTimer(self)
        timer.setInterval(20)  # period, in milliseconds
        timer.timeout.connect(self.gl.updateGL)
        timer.start()

    def openFile(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open file', '', "Mesh files (*.obj *.off *.stl *.ply)")
        mesh = om.read_trimesh(fname[0])
        self.gl.set_mesh(mesh)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = MainWindow()

    win.show()
    app.exec()
