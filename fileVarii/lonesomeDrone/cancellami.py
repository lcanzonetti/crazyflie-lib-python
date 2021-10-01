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
    while True:
        pygame.event.pump()
        sys.stdout.write('%s | Axes: ' % controller.get_name())
        for k in range(controller.get_numaxes()):
            sys.stdout.write('%d:%+2.2f ' % (k, controller.get_axis(k)))
        sys.stdout.write(' | Buttons: ')
        for k in range(controller.get_numbuttons()):
            sys.stdout.write('%d:%d ' % (k, controller.get_button(k)))
        sys.stdout.write('\n')
        time.sleep(0.1)
    


if __name__ == '__main__':
    joystickThread = threading.Thread(target=gamepadCommands).start()
 
   
    while True:
        pass
    PowerSwitch(uro).stm_power_down()
    print('Demo terminated!')




