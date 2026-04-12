import moderngl
from PyQt5 import QtCore
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import QTimer

import numpy as np
from pyrr import Matrix44
from computer_code.Ui.ArcBall import ArcBallUtil


class QGLControllerWidget(QOpenGLWidget):

    def __init__(self, parent=None):
        self.parent = parent
        super().__init__(parent)
        self.ctx = None
        super(QGLControllerWidget, self).__init__(parent)
        

    def initializeGL(self):
        QTimer.singleShot(0, self.init_mgl)

    def init_mgl(self):
        self.makeCurrent()
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
    def camera_helper(self,position, size, transform):
        # Define a simple pyramid frustum shape at the origin
        base = np.array([
            [-size, -size, size],
            [ size, -size, size],
            [ size,  size, size],
            [-size,  size, size]
        ])
        apex = np.array([0, 0, 0])
        # Lines from apex to base corners and around base
        lines = []
        for i in range(4):
            lines.append(apex)
            lines.append(base[i])
            lines.append(base[i])
            lines.append(base[(i+1)%4])
        camera_vertices = np.array(lines, dtype='f4')

        # Apply transformation if provided
        if transform is not None:
            if isinstance(transform, dict) and 'R' in transform and 't' in transform:
                # Compose 4x4 matrix from R and t
                R = np.asarray(transform['R'], dtype='f4')
                t = np.asarray(transform['t'], dtype='f4').reshape(3)
                mat = np.eye(4, dtype='f4')
                mat[:3, :3] = R
                mat[:3, 3] = t
                transform_mat = mat
            elif isinstance(transform, np.ndarray) and transform.shape == (4, 4):
                transform_mat = transform
            else:
                raise ValueError("transform must be a 4x4 numpy array or a dict with 'R' and 't'")
            # Homogeneous coordinates for transformation
            ones = np.ones((camera_vertices.shape[0], 1), dtype='f4')
            verts_hom = np.hstack([camera_vertices, ones])
            camera_vertices = (transform_mat @ verts_hom.T).T[:, :3]
        else:
            # Apply translation by position if no transform
            camera_vertices += np.array(position, dtype='f4')
        return camera_vertices

    def add_camera(self, position=(0, 0, 0), size=0.1, transform=None):
        """Adds a simple wireframe camera frustum to the view. Supports multiple cameras.
        Args:
            position: (x, y, z) tuple for camera position (used if transform is None).
            size: Size of the frustum.
            transform: Optional 4x4 transformation matrix (numpy array) or dict with 'R' and 't'.
        """
        
        camera_vertices = self.camera_helper(position, size, transform)
        # Initialize storage for multiple cameras if not present
        if not hasattr(self, 'camera_vertices_list'):
            self.camera_vertices_list = []
        self.camera_vertices_list.append(camera_vertices)

        # Concatenate all camera vertices for rendering
        all_vertices = np.concatenate(self.camera_vertices_list, axis=0)
        self.camera_vbo = self.ctx.buffer(all_vertices.tobytes())
        self.camera_vao = self.ctx.simple_vertex_array(
            self.prog, self.camera_vbo, 'in_position'
        )
        self.camera_vertex_count = len(all_vertices)
        self.has_camera = True
    def update_camera(self, index, position=None, transform=None):
        """
        Updates the position and/or transform of an existing camera.
        Args:
            index: Index of the camera to update.
            position: (x, y, z) tuple for new camera position (used if transform is None).
            transform: Optional 4x4 transformation matrix (numpy array) for rotation and translation.
        """
        if not hasattr(self, 'camera_vertices_list') or index >= len(self.camera_vertices_list):
            raise IndexError("Camera index out of range")

        size = 0.1  # Default size; you may want to store per-camera size if needed
        camera_vertices = self.camera_helper(position, size, transform)

        self.camera_vertices_list[index] = camera_vertices
        all_vertices = np.concatenate(self.camera_vertices_list, axis=0)
        self.camera_vbo = self.ctx.buffer(all_vertices.tobytes())
        self.camera_vao = self.ctx.simple_vertex_array(
            self.prog, self.camera_vbo, 'in_position'
        )
        self.camera_vertex_count = len(all_vertices)
    def add_point(self, position=(0, 0, 0), color=(1.0, 0.0, 0.0, 1.0), size=3):
        # TODO currently point size and color are global should not be this way 
        if len(position) != 3:
            return
        # Initialize storage for multiple points if not present
        if not hasattr(self, 'points_list')  :
            self.points_list = []
            self.point_colors = []
            self.point_size = size
        self.points_list.append(np.array(position, dtype='f4'))
        self.point_colors.append(color)
        # Concatenate all points for rendering
        all_points = np.vstack(self.points_list)
        self.point_vbo = self.ctx.buffer(all_points.tobytes())
        # Use the first color for all points if colors differ, or average
        if len(set(self.point_colors)) == 1:
            self.point_color = self.point_colors[0]
        else:
            self.point_color = tuple(np.mean(self.point_colors, axis=0))
        self.point_vao = self.ctx.simple_vertex_array(
            self.prog, self.point_vbo, 'in_position'
        )
        self.point_vertex_count = len(all_points)
        self.has_points = True

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
    def paintGL(self):
        if self.ctx is None:
            return
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

        # Draw camera if available
        if hasattr(self, 'has_camera') and self.has_camera:
            self.color.value = (0.0, 0.0, 1.0, 1.0)
            self.camera_vao.render(mode=moderngl.LINES, vertices=self.camera_vertex_count)

        # Draw points if available
        if hasattr(self, 'has_points') and self.has_points:
            self.color.value = self.point_color
            self.ctx.point_size = self.point_size
            self.point_vao.render(mode=moderngl.POINTS, vertices=self.point_vertex_count)
            self.color.value = (1.0, 1.0, 1.0, 0.8)
            if hasattr(self, 'vao'):
                self.vao.render()


    def resizeGL(self, width, height):
        if self.ctx is None:
            return
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

