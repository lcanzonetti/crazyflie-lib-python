#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#anger deck

# import pygame
import pygame
# Initialize pygame for joystick support
pygame.display.init()
pygame.joystick.init()
controller = pygame.joystick.Joystick(0)
controller.init()
import threading
import logging
import sys
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper
from cflib.utils.multiranger import Multiranger
from   cflib.utils.power_switch import PowerSwitch

MIN_DISTANCE      = 0.25
MAX_VELOCITY_XY   = 0.4
MAX_VELOCITY_Z    = 0.4
MAX_VELOCITY_YAW  = 90



uro =('radio://0/110/2M/E7E7E7E7EA')

comandi = {
    'destraSinistra':0,
    'avantiDietro': 0,
    'leftRight': 0,
    'changeHeight': 0
}

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

def is_close(range):
    distance = MIN_DISTANCE
    if range is None:
        return False
    else:
        return range < distance
    

def getGamepadCommands():
    pygame.event.pump()

    for k in range(controller.get_numaxes()):
        if k == 2: 
            # sys.stdout.write('%d:%+2.2f ' % (k, controller.get_axis(k)))
            comandi['destraSinistra'] = controller.get_axis(k) * -1.
        elif k == 3:
            comandi['avantiDietro'] = controller.get_axis(k) * -1.
        elif k == 1:
            comandi['changeHeight'] = controller.get_axis(k)
        elif k == 0:
            comandi['leftRight'] = controller.get_axis(k)
    # print (comandi)<


if __name__ == '__main__':
    # joystickThread = threading.Thread(target=gamepadCommands)
    cflib.crtp.init_drivers()
    PowerSwitch(uro).stm_power_up()
    time.sleep(3)
    cf = Crazyflie(rw_cache='./cache')
    print('hi!')
    with SyncCrazyflie(uro, cf=cf) as scf:
        with MotionCommander(scf, default_height=1) as motion_commander:
            with Multiranger(scf) as multiranger:
                keep_flying = True

                while keep_flying:
                    velocity_x     = 0.0
                    velocity_y     = 0.0
                    velocity_z     = 0.0
                    velocity_yaw   = 0.0
                    
                    getGamepadCommands()
                    
                    if comandi['destraSinistra'] != 0:
                        velocity_y = comandi['destraSinistra'] * MAX_VELOCITY_XY
                    if comandi['avantiDietro'] != 0:
                        velocity_x = comandi['avantiDietro'] * MAX_VELOCITY_XY
                    if comandi['changeHeight'] != 0:
                        velocity_z = comandi['changeHeight'] * MAX_VELOCITY_Z
                    if comandi['leftRight'] != 0:
                        velocity_yaw = comandi['leftRight'] * MAX_VELOCITY_YAW


                    if is_close(multiranger.front):
                        velocity_x -= MAX_VELOCITY_XY
                    if is_close(multiranger.back):
                        velocity_x += MAX_VELOCITY_XY
                    if is_close(multiranger.left):
                        velocity_y -= MAX_VELOCITY_XY
                    if is_close(multiranger.right):
                        velocity_y += MAX_VELOCITY_XY
                    if is_close(multiranger.up):
                        keep_flying = False

                    # print ('moving with speed x:%s\ty:%s\tz:%s\tyaw:%s' % (velocity_x, velocity_y, velocity_z, velocity_z))
                    motion_commander.start_linear_motion( velocity_x, velocity_y, velocity_z, velocity_yaw)
                    time.sleep(0.01)
    PowerSwitch(uro).stm_power_down()
    print('goodbye')