#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#test joystick

import pygame, sys, os
# Initialize pygame for joystick support
pygame.display.init()
pygame.joystick.init()
controller = pygame.joystick.Joystick(0)
controller.init()
# joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
# print (joysticks)
import time

 

MIN_DISTANCE      = 0.40
MAX_VELOCITY_XY   = 0.60
MAX_VELOCITY_Z    = 0.95
MAX_VELOCITY_YAW  = 120
 
comandi = {
    'destraSinistra':0,
    'avantiDietro': 0,
    'leftRight': 0,
    'changeHeight': 0
}
 
def getGamepadCommands():
    pygame.event.pump()

    for k in range(controller.get_numaxes()):
        sys.stdout.write('%d:%+2.2f ' % (k, controller.get_axis(k)))
        if k == 2: 
            comandi['destraSinistra'] = controller.get_axis(k) * -1.
        elif k == 3:
            comandi['avantiDietro'] = controller.get_axis(k) * -1.
        elif k == 1:
            comandi['changeHeight'] = controller.get_axis(k)
        elif k == 0:
            comandi['leftRight'] = controller.get_axis(k)
    print (comandi)


if __name__ == '__main__':
    print('hi!')
    while True:
        velocity_x     = 0.0
        velocity_y     = 0.0
        velocity_z     = 0.0
        velocity_yaw   = 0.0
        
        getGamepadCommands()
        
        
        if comandi['destraSinistra'] != 0:   velocity_y   = comandi['destraSinistra'] * MAX_VELOCITY_XY
        if comandi['avantiDietro']   != 0:   velocity_x   = comandi['avantiDietro']   * MAX_VELOCITY_XY
        if comandi['changeHeight']   != 0:   velocity_z   = comandi['changeHeight']   * MAX_VELOCITY_Z
        if comandi['leftRight']      != 0:   velocity_yaw = comandi['leftRight']      * MAX_VELOCITY_YAW
        print ('moving with speed x:%s\ty:%s\tz:%s\tyaw:%s' % (velocity_x, velocity_y, velocity_z, velocity_z))
        time.sleep(0.2)
        os.system("cls")
    print('goodbye') 