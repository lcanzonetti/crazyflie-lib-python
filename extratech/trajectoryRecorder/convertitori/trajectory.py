from scipy import interpolate
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
HEIGHT = 1
SET_POINTS = 25


sequenza =\
{
    0: {"TC": "00:01:00:00", "x": 0,    "y": 0,   "z": 0}, 
    1: {"TC": "00:01:00:00", "x": 0,    "y": 0,   "z": 0.5}, 
    2: {"TC": "00:01:03:00", "x": 0,    "y": 0,   "z": 1}, 
    3: {"TC": "00:01:04:00", "x": 1,    "y": -1., "z": 1.1}, 
    4: {"TC": "00:01:06:00", "x": 0.8,  "y": 0.,  "z": 0.9}, 
    5: {"TC": "00:01:08:00", "x": -1.2, "y": 1.5, "z": 1.9}, 
    6: {"TC": "00:01:10:00", "x": -1.4, "y": 1.6, "z": 0.7}, 
    7: {"TC": "00:01:12:00", "x": 0,    "y": 1.,  "z": 0} 
}


def main():
    lista = []
    for k in range(len(sequenza)-1):
        lista.extend( generate_trajectory_curve(sequenza[k], sequenza[k+1]))
    numpai_arrai = np.array(lista).T    
    fig          = plt.figure()
    ax           = fig.add_subplot(111, projection = '3d')
    
    ax.plot(numpai_arrai[0], numpai_arrai[1], numpai_arrai[2], marker = 'x')
    ax.scatter(*numpai_arrai.T[0], color = 'red', marker='o')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.show()
 
def generate_trajectory_curve(start, end):
    """
    Calculates a curve between the current position and the target.
    """
    # start = self.copter_pos
    # end = self.lz_pos
    mid = {'x': (start['x'] + end['x'])/2,
            'y': (start['y'] + end['y'])/2,
            'z': max(start['z'], end['z']) + HEIGHT}

    x = [start['x'], mid['x'], end['x']]
    y = [start['y'], mid['y'], end['y']]
    z = [start['z'], mid['z'], end['z']]

    (tck, u) = interpolate.splprep([x, y, z], k=2)
    t = np.linspace(0, 1, SET_POINTS)
    points = interpolate.splev(t, tck)
    robba  = []
    for i in range(SET_POINTS):
        x = round(points[0][i], 3)
        y = round(points[1][i], 3)
        z = round(points[2][i], 3)
        # robba[i] =  ({'x': x, 'y': y, 'z': z})
        robba.append ([x,y,z])
    print(robba)
    print()
    return robba

def _format_data(self, data):
        return {
            'id': data['id'],
            'x': data['pos'][0],
            'y': data['pos'][1],
            'z': data['pos'][2],
            'angle': data['angle']
        }




if __name__ == '__main__':
    main()
