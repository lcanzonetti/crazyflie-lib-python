#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, sys, threading, logging
from getkey import getkey, keys
from itertools import cycle
from   osc4py3.as_eventloop  import *
from   osc4py3               import oscmethod as osm
from   osc4py3               import oscbuildparse

porta = 9200
loop = cycle(r"-\|/")
bufferone         = {}
timecode          = '00:00:00:00'

# replace with your function
def func():
    print("running ...", next(loop), end='\r', flush=True)

def setRequestedPos(address, args):
    # print(address)
    # print(args)
    global timecode
    x = address.split('/')
    # print (x)
    y = x[2].split('_')
    iddio = int(y[1])
    # print(iddio)
    # timecode   = args[0]
    print('Ciao sono il drone %s e dovrei andare a X %s, Y %s, Z %s' %(iddio,round(float(args[0]),3), round(float(args[1]),3), round(float(args[2]),3)))

    bufferone[iddio].requested_X = round(float(args[1]),3)
    bufferone[iddio].requested_Y = round(float(args[2]),3)
    bufferone[iddio].requested_Z = round(float(args[3]),3)
    
def setRequestedCol(address, args):
    # print(address)
    # print(args)
    x = address.split('/')
    y = x[2].split('_')
    iddio = int(y[1])

    bufferone[iddio].requested_R = args[0]
    bufferone[iddio].requested_G = args[1]
    bufferone[iddio].requested_B = args[2]
    print('Ciao sono il drone %s e dovrei avere il colore R %s, G %s, B %s' %(iddio, args[0],  args[1], args[2] ))



def recorda():
    try:
        input("press enter to start recording and q to stop")
        # logging.basicConfig(format='%(asctime)s - %(threadName)s ø %(name)s - '  '%(levelname)s - %(message)s')
        # logger = logging.getLogger("osc")
        # logger.setLevel(logging.DEBUG)
        # osc_startup(logger=logger)
        osc_startup()
        osc_udp_server("0.0.0.0", porta,   "receivingServer")
        ###########################  single fella requested position
        osc_method("/notch/drone*/pos",   setRequestedPos,      argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)
        osc_method("/notch/drone*/col", setRequestedCol,      argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)
        print("Recording Server started on port %d. Press q terminate and save." % (porta))
    except Exception as err:
         print(str(err))


    while True:
        try:
            time.sleep(0.05)
            func()
            osc_process()
            
        except KeyboardInterrupt:
            print('Recording Done')
            osc_terminate()
            sys.exit()
 
def faiIlBufferon():
    global bufferone
    for i in range (0,20):
        bufferone[i] = bufferDrone(i)

class bufferDrone():
    def __init__(self, ID, ):
        self.ID          = int(ID)
        self.name        = 'bufferDrone'+str(ID)
        self.requested_X            = 0.0
        self.requested_Y            = 0.0
        self.requested_Z            = 1.0
        self.requested_R            = 0
        self.requested_G            = 0
        self.requested_B            = 0
        self.yaw                   = 0.0

if __name__ == '__main__':
    faiIlBufferon()
    OSCRefreshThread      = threading.Thread(target=recorda).start()
    # sendPose()
    while True:
        time.sleep(1)
        pass
