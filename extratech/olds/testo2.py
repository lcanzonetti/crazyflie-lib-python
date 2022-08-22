import multiprocessing
import random
from multiprocessing import Process, Queue
import time
import sys
import pytimecode
# import finestrina
import threading
from threading import Thread
import math

import pygame
pygame.init()
joysticks = []
buttons = []
clock = pygame.time.Clock()
keepPlaying = True
jojo = None

 

if __name__=='__main__':
    # a = [0, 0, 0] 
    # b = [4,4,4] 
    # Calculate Euclidean distance
    # print (math.dist(a,b))

    # for al the connected joysticks

    try:
        for i in range(0, pygame.joystick.get_count()):
            # create an Joystick object in our list
            joysticks.append(pygame.joystick.Joystick(i))
            # initialize them all (-1 means loop forever)
            joysticks[-1].init()
            jojo = joysticks[-1]
            buttons = joysticks[-1].get_numbuttons()

            # print a statement telling what the name of the controller is
            print ("Detected joystick "),joysticks[-1].get_name(),"'"
    except:
        print('maaa, er joystick?')
    

    while keepPlaying:
        clock.tick(60)
        for event in pygame.event.get():
            pass
            # The 0 button is the 'a' button, 1 is the 'b' button, 2 is the 'x' button, 3 is the 'y' button
            if event.type == pygame.JOYBUTTONDOWN:
                for i in range(buttons):
                    button = jojo.get_button(i)
                    print("Button {:>2} value: {}".format(i, button))
                # print("Joystick button pressed.")
            if event.type == pygame.JOYBUTTONUP:
                print("Joystick button released.")

 
     