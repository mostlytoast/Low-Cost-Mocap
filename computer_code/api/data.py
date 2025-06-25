from Singleton import Singleton
@Singleton
class Data:
    # @profile
    def __init__(self):

        self.to_world_coords_matrix= [
    ]
        self.camera_poses = {}