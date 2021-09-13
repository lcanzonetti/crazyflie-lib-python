#rf 2021
import threading
import multiprocessing

import time
from   multiprocessing.connection import Listener
from   multiprocessing.connection import Client

from   colorama              import Fore, Back, Style  
from   osc4py3.as_eventloop  import *
from   osc4py3               import oscmethod as osm
from   osc4py3               import oscbuildparse
from   random                import random, uniform
import logging

finished = False
# bufferon = {}

class Feedbacco():
    def __init__(self, eventoFinaleTremendo):
        self.OSC_SENDING_IP   = "192.168.10.255"
        self.SENDING_PORT     = 9203
        self.RECEIVING_PORT   = 6000
        self.finished         = eventoFinaleTremendo
        self.start()

    def sendPose(self, robbaVaria):
        iddio    = str(robbaVaria[0])
        ixxa     = robbaVaria[1]
        ipsila   = robbaVaria[2]
        zedda    = robbaVaria[3]
        batteria = float(robbaVaria[4])
        # print ('direi a tutti he il drogno %s sta a  %s  |  %s  |  %s   con batteria %s' % (iddio, ixxa, ipsila, zedda, batteria))
        coordinate  = oscbuildparse.OSCMessage("/feedback/" + iddio + "/pos", ",fff",   [ixxa,ipsila,zedda])
        robba       = oscbuildparse.OSCMessage("/feedback/" + iddio + "/battery", ",f",  [batteria])
        bandoleon   = oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, [coordinate, robba]) 
        osc_send(bandoleon, "feedbackClient")
    
    def start(self):

        address = ('127.0.0.1', self.RECEIVING_PORT)
        listener = Listener(address)

        print('feeddabcker yeah')
        # self.bufferone = robba
        # logging.basicConfig(format='%(asctime)s - %(threadName)s ø %(name)s - ' '%(levelname)s - %(message)s')
        # logger = logging.getLogger("osc")
        # logger.setLevel(logging.DEBUG)
        # osc_startup(logger=logger)

        def oscLoop():
            connessione = listener.accept()

            while not self.finished.is_set():
                osc_process()
                msg = connessione.recv()
                if msg == 'fuck you':
                    self.finished.set()
                    break
                else:
                    self.sendPose(msg)
                time.sleep(0.01)
            # Properly close the system.
            print('\nanche il feedbacker se ne va')
            osc_terminate()
            listener.close()
        
        osc_startup()
        osc_broadcast_client(self.OSC_SENDING_IP, self.SENDING_PORT, "feedbackClient")
        print(Fore.YELLOW + 'osc feedbacker sending on %s'%  self.SENDING_PORT)
        tridio = threading.Thread(target=oscLoop).start()
        ###########################  single fella
        

 
#cancellami:

def fammeNesempio(carlo):
    print('minchia')
    def daje():
        print('ad esempio')
        global finished
        conto = 5
        while conto > 0:
            carlo.sendPose([int(random()*10), round(random()*10,3), round(random()*10,3), round(random()*10,3), round(random()*10,2)])
            conto -= 1
            time.sleep(1)
        processes_exit_event.set()
    OSCesempio        = threading.Thread(target=daje,daemon=True).start()




########## main
if __name__ == '__main__':
    processes_exit_event = multiprocessing.Event()
    address = ('127.0.0.1', 6000)
    istanza = Feedbacco(processes_exit_event)
    esempiatore = fammeNesempio(istanza)

    time.sleep(3)
    connectionToFeedbackProcess = Client(address)
    connectionToFeedbackProcess.send('fuck your mother')

    while not finished:
        pass


