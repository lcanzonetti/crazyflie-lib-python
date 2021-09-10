#rf 2021
from multiprocessing import connection
import threading
import time
import repeatedTimer as rp
from multiprocessing.connection import Listener

from   colorama              import Fore, Back, Style  
from   osc4py3.as_eventloop  import *
from   osc4py3               import oscmethod as osm
from   osc4py3               import oscbuildparse
from   random                import random, uniform
import logging

finished = False
# bufferon = {}

class feedbacco():
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
        address = ('localhost', self.RECEIVING_PORT)
        listener = Listener(address)
        connessione = listener.accept()
        print('feeddabcker yeah')
        # self.bufferone = robba
        # logging.basicConfig(format='%(asctime)s - %(threadName)s ø %(name)s - ' '%(levelname)s - %(message)s')
        # logger = logging.getLogger("osc")
        # logger.setLevel(logging.DEBUG)
        # osc_startup(logger=logger)

        def daje():
            while not self.finished.is_set():
                osc_process()
                msg = connessione.recv()
                self.sendPose(msg)
                time.sleep(0.01)
            # Properly close the system.
            print('anche il feedbacker se ne va')
            osc_terminate()
            listener.close()
        
        osc_startup()
        osc_broadcast_client(self.OSC_SENDING_IP, self.SENDING_PORT, "feedbackClient")
        print(Fore.YELLOW + 'osc feedbacker sending on %s'%  self.SENDING_PORT)
        tridio = threading.Thread(target=daje).start()
        ###########################  single fella
        

 
#cancellami:

def fammeNesempio(carlo):
    def daje():
        global finished
        conto = 5
        while conto > 0:
            carlo.sendPose([int(random()*10), round(random()*10,3), round(random()*10,3), round(random()*10,3), round(random()*10,2)])
            conto -= 1
            time.sleep(1)
        finished = True
    # while True:
    #     print ('tipo: ', str(bufferon[0].requested_X))
    #     print ('tipo: ', str(bufferon[1].requested_X))
    #     print ('tipo: ', str(bufferon[2].requested_X))
    #     print ('tipo: ', str(bufferon[3].requested_X))
    #     print ('tipo: ', str(bufferon[4].requested_X))
    #     print ('tipo: ', str(bufferon[5].requested_X))
    #     print ('tipo: ', str(bufferon[6].requested_X))
    #     print ('tipo: ', str(bufferon[7].requested_X))
    #     print ('tipo: ', str(bufferon[8].requested_X))
    #     time.sleep(1)
    OSCesempio        = threading.Thread(target=daje,daemon=True).start()
# OSCRefreshThread  = threading.Thread(target=gino.main)
# OSCRefreshThread.start()
# OSCRefreshThread.join()



########## main
if __name__ == '__main__':
    # print(bufferon)
    gino = feedbacco()
    gino.start()
    carlo = threading.Thread(target=fammeNesempio, args=[gino]).start()
    while not finished:
        pass


