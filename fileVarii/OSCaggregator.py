#rf 2021
import threading
import time
import repeatedTimer as rp

from   colorama              import Fore, Back, Style  
from   osc4py3.as_allthreads import *
from   osc4py3               import oscmethod as osm
from   osc4py3               import oscbuildparse
from   random                import uniform

finished = False
bufferon = {}


class Aggregator():
    def __init__(self):
        self.OSC_IP           = "127.0.0.1"
        self.SENDING_PORT     = 9200
        self.RECEIVING_PORT   = 9202
        self.finished         = False
        self.bufferone        = {}

    def setRequested(self, add, val):
        # print(add, val)

        iddio     = int(add[-3])
        value     = round(val,3)
        parametro = 'requested_' + add[-1]
        setattr(self.bufferone[iddio], parametro, value)
        # print ('setting: ', iddio, parametro, value)
        # print(self.bufferone[iddio].requested_X)


    def main(self, robba):
        print('robba')
        self.bufferone = robba
        # self.bufferone.pop(0)
        # self.bufferone.pop(1)
        # self.bufferone.pop(2)
        # self.bufferone.pop(3)
        # self.bufferone.pop(4)
        # self.bufferone.pop(5)
        # self.bufferone.pop(6)
        # self.bufferone.pop(7)
        # print(self.bufferone)

        global finished 
       
        osc_startup(execthreadscount=20)
        osc_udp_server("0.0.0.0", self.RECEIVING_PORT,               "aggregatingServer")
        print(Fore.YELLOW + 'osc aggegator receiving on %s'%  self.RECEIVING_PORT)

        ###########################  single fella
        osc_method("/notch/drone*/X",   self.setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
        osc_method("/notch/drone*/Y",   self.setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
        osc_method("/notch/drone*/Z",   self.setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
        osc_method("/notch/drone*/R",   self.setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
        osc_method("/notch/drone*/G",   self.setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
        osc_method("/notch/drone*/B",   self.setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)

        while not finished:
            osc_process()
            time.sleep(0.1)
        # Properly close the system.
        osc_terminate()


def faiIlBufferon():
    for i in range (0,20):
        bufferon[i] = bufferDrone(i)





class bufferDrone():
    def __init__(self, ID, ):
        self.ID          = int(ID)
        self.name        = 'bufferDrone'+str(ID)
        
        self.requested_X            = 0.0
        self.requested_Y            = 0.0
        self.requested_Z            = 0.0
        self.requested_R            = 0.0
        self.requested_G            = 0.0
        self.requested_B            = 0.0
        self.yaw                    = 0.0

########## main
if __name__ == '__main__':
    faiIlBufferon()
    # print(bufferon)
    gino = Aggregator(bufferon)
    print(gino.bufferone)
    print('porco il clero')

#cancellami:

    def fammeNesempio():
        global bufferon
        while True:
            print ('tipo: ', str(bufferon[0].requested_X))
            print ('tipo: ', str(bufferon[1].requested_X))
            print ('tipo: ', str(bufferon[2].requested_X))
            print ('tipo: ', str(bufferon[3].requested_X))
            print ('tipo: ', str(bufferon[4].requested_X))
            print ('tipo: ', str(bufferon[5].requested_X))
            print ('tipo: ', str(bufferon[6].requested_X))
            print ('tipo: ', str(bufferon[7].requested_X))
            print ('tipo: ', str(bufferon[8].requested_X))
            time.sleep(1)
    OSCesempio        = threading.Thread(target=fammeNesempio,daemon=True).start()
    OSCRefreshThread  = threading.Thread(target=gino.main)
    OSCRefreshThread.start()
    OSCRefreshThread.join()
