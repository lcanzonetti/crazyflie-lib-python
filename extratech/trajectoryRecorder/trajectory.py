from re import A
import zmq
from threading import Thread
from scipy import interpolate
from pprint import pprint
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
COPTER_ID = 1
LZ_ID = 0
ABOUT_TRHESHOLD = 0.1
HEIGHT = 1
SET_POINTS = 25


class CrazyTrajectory(Thread):

    def __init__(self, plotter=None):
        Thread.__init__(self)

        # self.context = context = zmq.Context()
        # self.camera_con = context.socket(zmq.SUB)
        # self.camera_con.connect('tcp://127.0.0.1:7777')
        # self.camera_con.setsockopt_string(zmq.SUBSCRIBE, '')

        # self.controller_con = context.socket(zmq.PUSH)
        # self.controller_con.connect('tcp://127.0.0.1:5124')
        self.copter_pos = None
        self.lz_pos = None
        self.plotter = plotter
        self.last_drawn_pos = None

    def run(self):
        while not self.copter_pos or not self.lz_pos:
            data = self.camera_con.recv_json()
            if 'id' not in data:
                print('Data is missing "id": %s' % data)
            elif data['id'] == COPTER_ID:
                self.last_drawn_pos = self.copter_pos = self._format_data(data)
            elif data['id'] == LZ_ID:
                self.lz_pos = self._format_data(data)
            else:
                print('Invalid id')

        if self.plotter:
            self.plotter.set_endpoints(self.copter_pos, self.lz_pos)
            points = list(self._generate_trajectory_curve())
            self.plotter.add_trajectory(points)

        input("Trajectory generated; press enter to proceed...")

        curve = self._generate_trajectory_curve()
        self.next_pos = next(curve)

        while not self._is_at_lz():
            data = self.camera_con.recv_json()
            if data['id'] == COPTER_ID:
                self.copter_pos = self._format_data(data)
                if self.plotter and not self._is_at_pos(self.copter_pos,
                                                        self.last_drawn_pos):
                    self.plotter.add_copter_point(self.copter_pos)
                    self.last_drawn_pos = self.copter_pos
            else:
                continue
            if self._is_at_pos(self.copter_pos, self.next_pos):
                self.next_pos = next(curve, self.lz_pos)
                self.controller_con.send_json({'set-points': self.next_pos})
        print('Trajectory completed!')

    def _generate_trajectory_curve(self, start, end):
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

        return robba

    def _aboutEquals(self, a, b):
        return abs(a - b) < ABOUT_TRHESHOLD

    def _is_at_pos(self, p1, p2):
        return (self._aboutEquals(p1['x'], p2['x']) and
                self._aboutEquals(p1['y'], p2['y']) and
                self._aboutEquals(p1['z'], p2['z']))

    def _is_at_lz(self):
        return self._is_at_pos(self.copter_pos, self.lz_pos)

    def _format_data(self, data):
        return {
            'id': data['id'],
            'x': data['pos'][0],
            'y': data['pos'][1],
            'z': data['pos'][2],
            'angle': data['angle']
        }

sequenza =\
{
    0: {"TC": "00:01:00:00", "x": 0,   "y": 0,   "z": 0}, 
    1: {"TC": "00:01:00:00", "x": 0,   "y": 0,   "z": 0.5}, 
    2: {"TC": "00:01:03:00", "x": 0,   "y": 0,   "z": 1}, 
    3: {"TC": "00:01:04:00", "x": 1,   "y": -1., "z": 1.1}, 
    4: {"TC": "00:01:06:00", "x": 0.8, "y": 0., "z": 0.9}, 
    5: {"TC": "00:01:08:00", "x": -1.2, "y": 1.5, "z": 1.9}, 
    6: {"TC": "00:01:10:00", "x": -1.4, "y": 1.6, "z": 0.7}, 
    7: {"TC": "00:01:12:00", "x": 0,   "y": 1., "z": 0} 
}

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np



if __name__ == '__main__':
    gino = CrazyTrajectory()
    edoardo = []
    for k in range(len(sequenza)-1):
        edoardo.extend(gino._generate_trajectory_curve(sequenza[k], sequenza[k+1]))
    pini = np.array(edoardo).T    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection = '3d')
    
    ax.plot(pini[0], pini[1], pini[2], marker = 'x')
    ax.scatter(*pini.T[0], color = 'red', marker='o')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.show()