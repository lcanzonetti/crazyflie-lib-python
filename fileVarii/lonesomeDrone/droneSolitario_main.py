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


uro =('radio://0/110/2M/E7E7E7E7EA')

comandi = {
    'ics':0,
    'ypsilon': 0,
    'turnLeft': 0,
    'turnRight': 0,
    'changeHeight': 0
}

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

def is_close(range):
    MIN_DISTANCE = 0.40  # m

    if range is None:
        return False
    else:
        return range < MIN_DISTANCE
    

def gamepadCommands():
      # Get next pygame event
    pygame.event.pump()

    # sys.stdout.write('%s | Axes: ' % controller.get_name())

    for k in range(controller.get_numaxes()):
        if k == 0: 
            # sys.stdout.write('%d:%+2.2f ' % (k, controller.get_axis(k)))
            comandi['ics'] = controller.get_axis(k)
        elif k == 1:
            comandi['ypsilon'] = controller.get_axis(k)
        elif k == 3:
            comandi['changeHeight'] = controller.get_axis(k)
        elif k == 4:
            comandi['turnLeft'] = controller.get_axis(k)
        elif k == 5:
            comandi['turnRight'] = controller.get_axis(k)
    print (comandi)
    # sys.stdout.write(' | Buttons: ')
    # for k in range(controller.get_numbuttons()):
    #     sys.stdout.write('%d:%d ' % (k, controller.get_button(k)))
    # sys.stdout.write('\n')


if __name__ == '__main__':
    joystickThread = threading.Thread(target=gamepadCommands)
    # Initialize the low-level drivers
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
                    VELOCITY   = 0.7
                    velocity_x = 0.0
                    velocity_y = 0.0

                    if is_close(multiranger.front):
                        velocity_x -= VELOCITY
                    if is_close(multiranger.back):
                        velocity_x += VELOCITY

                    if is_close(multiranger.left):
                        velocity_y -= VELOCITY
                    if is_close(multiranger.right):
                        velocity_y += VELOCITY

                    if is_close(multiranger.up):
                        keep_flying = False

                    motion_commander.start_linear_motion(
                        velocity_x, velocity_y, 0)
                    gamepadCommands()
                    time.sleep(0.08)
    # while True:
    #     gamepadCommands()
    #     time.sleep(0.08)
    PowerSwitch(uro).stm_power_down()
    print('Demo terminated!')




