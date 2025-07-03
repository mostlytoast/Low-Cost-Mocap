import json

import numpy as np


data = [{'R': np.array([[1., 0., 0.],
       [0., 1., 0.],
       [0., 0., 1.]]), 't': [0.23657030097703047, -0.8532631852565995, 0.8153589060348242]}, {'R': np.array([[-0.58807735,  0.72425855, -0.36002024],
       [-0.25896612,  0.25308268,  0.93214039],
       [ 0.76622554,  0.6414037 ,  0.03872624]]), 't': [0.23657030097703047, -0.8532631852565995, 0.8153589060348242]}]
def serialize(pose):
    out = []
    for cam in pose: 
        out.append({'R': cam['R'].tolist(),'t': cam['t']})
    return out


with open("/home/tom/Projects/new-Low-Cost-Mocap/Low-Cost-Mocap/calib3.json","w") as f:
    
    json.dump(serialize(data),f)