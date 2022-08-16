#rf 2021
import threading
import multiprocessing

import time
from   multiprocessing.connection import Listener
from   multiprocessing.connection import Client

from   colorama              import Fore, Back, Style
from   colorama              import init as coloInit  
coloInit(convert=True)

import socket

from   osc4py3.as_eventloop  import *
from   osc4py3               import oscmethod as osm
from   osc4py3               import oscbuildparse
from   random                import random, uniform
import logging
logging.basicConfig(format='%(asctime)s - %(threadName)s ø %(name)s - '
    '%(levelname)s - %(message)s')
logger = logging.getLogger("osc")
logger.setLevel(logging.DEBUG)

finished = False
class Feedbacco():
    def __init__(self, ID, eventoFinaleTremendo, sendingIP, sendingPort,receiving_port):
        self.OSC_SENDING_IP   = sendingIP
        self.sendingPort      = sendingPort
        self.port             = receiving_port
        self.finished         = eventoFinaleTremendo
        self.ID               = ID
        # self.start()
 
    def sendPose(self, stuff):
        iddio    = str(stuff[0])
        ixxa     = stuff[1]
        ipsila   = stuff[2]
        zedda    = stuff[3]
        batteria = float(stuff[4])
        yawa     = stuff[5]

        # print ('direi a tutti he il drogno %s sta a  %s  |  %s  |  %s   con batteria %s' % (iddio, ixxa, ipsila, zedda, batteria))
        coordinate  = oscbuildparse.OSCMessage("/feedback/" + iddio + "/pos", ",fff",   [ixxa,ipsila,zedda])
        robba       = oscbuildparse.OSCMessage("/feedback/" + iddio + "/battery", ",ff",  [batteria,yawa])
        bandoleon   = oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, [coordinate, robba]) 
        osc_send(bandoleon, "feedbackClient")
  
    def start(self):
        address = ('127.0.0.1', self.port)
        listener = Listener(address)
        # print('feeddabcker yeah on port %s' % str(self.port))
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
            print('\nFeedbacker process for drogno %s leaving.' % self.ID)
            osc_terminate()
            listener.close()
        
        osc_startup()
        # osc_startup(logger=logger)

        osc_broadcast_client(self.OSC_SENDING_IP, self.sendingPort, "feedbackClient")
        print(Fore.YELLOW + 'osc feedbacker for drogno %s sending on %s %s'%  (self.ID, self.OSC_SENDING_IP,self.sendingPort))
        tridio = threading.Thread(target=oscLoop).start()
        ###########################  single fella
        

class CompanionFeedbacco():
    def __init__(self, cuia, sendingIP, sendingPort):
        self.sendingIP       = sendingIP
        self.sendingPort     = sendingPort
        self.cuia            = cuia
        print('companion OSC feedback process initalized on %s %s' %  (self.sendingIP,  self.sendingPort))

    def sendCompanionFeedback(self, stuff):
        bandoleon   = oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, stuff) 
        osc_send(bandoleon, "feedbackClient")
  
    def start(self):
        def oscLoop():
            while True:
                osc_process()
                msg = self.cuia.get()
                if msg == 'fuck you':
                    # self.finished.set()
                    break
                else:
                    self.sendCompanionFeedback(msg)
                time.sleep(0.01)
            # Properly close the system.
            self.cuia.close()
            # self.cuia.join_thread()
            osc_terminate()
            print('\nanche il companion feedbacker se ne va')

        osc_startup()
        # osc_startup(logger=logger)

        
        # osc_broadcast_client(self.sendingIP, self.sendingPort, "feedbackClient")
        osc_udp_client(self.sendingIP, self.sendingPort, "feedbackClient")
        print(Fore.YELLOW + 'companion osc feedbacker sending on %s'%  self.sendingPort)
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
    istanza = Feedbacco(processes_exit_event, 6000)
    esempiatore = fammeNesempio(istanza)

    time.sleep(3)
    connectionToFeedbackProcess = Client(address)
    connectionToFeedbackProcess.send('fuck your mother')

    while not finished:
        pass


