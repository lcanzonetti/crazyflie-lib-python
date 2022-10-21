# -*- coding: utf-8 -*-
#rf 2022

# built-ins
import random, threading, time, signal, sys
# numpy and matlib
from plotterie.utils import ypr_to_R
from plotterie.uav   import Uav
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
# OSC
from   osc4py3.as_eventloop  import *
from   osc4py3               import oscmethod as osm
# custom
import GLOBALS as GB


is_test = False
quanti_vizzidroni     = 6


insieme_di_vizzidroni = []

# Initiate the plot
plt.style.use('seaborn')
fig             = plt.figure()
ax              = fig.add_subplot(projection='3d')
xmin, xmax      = -3, 3
ymin, ymax      = -3, 3
zmin, zmax      = 0, 3
arm_length      = 0.1  # in meters
yaw_pitch_roll  = np.zeros(3)
rotation_matrix = ypr_to_R(yaw_pitch_roll, degrees=True)


finished        = threading.Event()

def update_plot(frame):
    # print('frame %s ' % frame)
    ax.clear()
    for drogno in insieme_di_vizzidroni:    
        drogno.draw_yourself_useful()
  
# generates new pose to test shit 
def generatore():
    while not finished.is_set() and is_test:
        time.sleep(0.1)
        for vizzo in insieme_di_vizzidroni:
            vizzo.requested_X += random.uniform(-0.2, 0.2)
            vizzo.requested_Y += random.uniform(-0.2, 0.2)
            vizzo.requested_Z += random.uniform(-0.2, 0.2)
        
# function get called in the OSC loop when a new pose bundle lands
def setRequestedPos(address, args):
    x = address.split('/')
    y = x[2].split('_')
    iddio = int(y[1])
    insieme_di_vizzidroni[iddio].requested_X = float(args[1])
    insieme_di_vizzidroni[iddio].requested_Y = float(args[2])
    insieme_di_vizzidroni[iddio].requested_Z = float(args[3])
# start OSC to pose and orientation from telemetry
def start_OSC_receiver():
    osc_startup()
    osc_udp_server('0.0.0.0', GB.FEEDBACK_SENDING_PORT,  "vizServer")
    osc_method("/feedback/drone*/pos",   setRequestedPos, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)
    while not GB.eventi.get_thread_exit_event().is_set():
        time.sleep(GB.OSC_PROCESS_RATE)
        osc_process()
    # Properly close the system.
    print('chiudo OSC')
    osc_terminate()
#  just a vizzidrone instantiator 
def crea_dei_vizzidroni():
    for i in range (0,quanti_vizzidroni):
        insieme_di_vizzidroni.append(Vizzidrone(i, ax))
#  class wrapping data and geometry, plus a drwing function
class Vizzidrone():
    def __init__(self, ID, ax):
        self.ID          = int(ID)
        self.name        = 'vizzidrone_'+str(ID)
        self.requested_X            = 0.0
        self.requested_Y            = 0.0
        self.requested_Z            = 0.0
        self.requested_R            = 0
        self.requested_G            = 0
        self.requested_B            = 0
        self.yaw                    = 0.0
        self.ax                     = ax
        self.uav                    = None

    def start(self):
        self.uav      = Uav(self.ax, arm_length, self.ID)
    
    def draw_yourself_useful(self):
        # These limits must be set manually since we use
        # a different axis frame configuration than the
        # one matplotlib uses.
        xyz = np.array ([self.requested_X, self.requested_Y,self.requested_Z]) 
        # print('sposto il drogno %s a %s, %s:' % (self.name, xyz, rotation_matrix))
        self.uav.draw_at(xyz, rotation_matrix)  

        self.ax.set_xlim([xmin, xmax])
        self.ax.set_ylim([ymax, ymin])
        self.ax.set_zlim([zmax, zmin])
        pass
# 
def main():
    signal.signal(signal.SIGINT, exit_signal_handler) 
    crea_dei_vizzidroni()
    for vizzidrone in insieme_di_vizzidroni: 
        vizzidrone.start()
    # start_OSC_receiver()
    time.sleep(2)
    # Run the simulation
    ani         = animation.FuncAnimation(fig, update_plot, interval=100)
    # generate new test values
    genera_robe = threading.Thread(target=generatore).start()
    plt.show()

    while not finished.is_set():
        time.sleep(0.1)
#  working already?
def exit_signal_handler(signum, frame):
    finished.set()
    sys.exit("Putin merda")
# 
if __name__ == '__main__':
    main()
   
        