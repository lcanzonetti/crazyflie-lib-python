""" 

import random
import threading, time

buffer ={
    'X': 0,
    'Y': 0,
    'Z': 0
}

 

from pyplot3d.uav import Uav
from pyplot3d.utils import ypr_to_R

import numpy as np
import matplotlib.pyplot as plt

plt.style.use('seaborn')

# initialize plot
fig = plt.figure()
ax = fig.gca(projection='3d')

arm_length = 0.05  # in meters
uav = Uav(ax, arm_length)



def generatore():
    global buffer
    
    while True:
        time.sleep(0.1)
        buffer['X'] += random.uniform(-0.2, 0.2)
        buffer['Y'] += random.uniform(-0.2, 0.2)
        buffer['Z'] += random.uniform(-0.2, 0.2)
        uav.draw_at([buffer['Y'],  buffer['X'], buffer['Z']], ypr_to_R([np.pi/2.0, 0, 0]))



plt.show()
genera_robe = threading.Thread(target=generatore).start()
"""

from pyplot3d.utils import ypr_to_R
from pyplot3d.uav   import Uav

from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D

import matplotlib.pyplot as plt
import numpy as np
    
def update_plot(i, x, R):
    uav_plot.draw_at(x[:, i], R[:, :, i])
    
    # These limits must be set manually since we use
    # a different axis frame configuration than the
    # one matplotlib uses.
    xmin, xmax = -2, 2
    ymin, ymax = -2, 2
    zmin, zmax = -2, 2

    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymax, ymin])
    ax.set_zlim([zmax, zmin])

# Initiate the plot
plt.style.use('seaborn')

fig = plt.figure()
ax = fig.gca(projection='3d')

arm_length = 0.24  # in meters
uav_plot = Uav(ax, arm_length)


# Create some fake simulation data
steps = 60
t_end = 1

x = np.zeros((3, steps))
x[0, :] = np.arange(0, t_end, t_end / steps)
x[1, :] = np.arange(0, t_end, t_end / steps) * 2

R = np.zeros((3, 3, steps))
for i in range(steps):
    ypr = np.array([i, 0.1 * i, 0.0])
    R[:, :, i] = ypr_to_R(ypr, degrees=True)


# Run the simulation
ani = animation.FuncAnimation(fig, update_plot, frames=steps, fargs=(x, R,))

plt.show()