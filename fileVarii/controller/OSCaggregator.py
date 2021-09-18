#rf 2021
import threading
import time 
from   multiprocessing import Process, Queue, Event

from   colorama              import Fore, Back, Style
from   colorama              import init as coloInit  
coloInit(convert=True)

from   osc4py3.as_eventloop  import *
from   osc4py3               import oscmethod as osm
from   osc4py3               import oscbuildparse
from   random                import uniform
import logging
logging.basicConfig(format='%(asctime)s - %(threadName)s ø %(name)s - '
    '%(levelname)s - %(message)s')
logger = logging.getLogger("osc")
logger.setLevel(logging.DEBUG)

class Aggregator():
    def __init__(self, eventoFineDeMondo, coda, receivingPort, bufferone, oscProcessRate):
        self.RECEIVING_PORT   = receivingPort
        self.finished         = eventoFineDeMondo
        self.bufferone        = bufferone
        self.coda             = coda
        self.oscProcessRate   = oscProcessRate

    def setRequested(self, addr, val):
        # print(addr, val)
        iddio     = int(addr[-3])
        value     = round(val,3)
        parametro = 'requested_' + addr[-1]
        setattr(self.bufferone[iddio], parametro, value)
    
    def sendCompleteFrame(self, addr, tc):
        # self.coda.put('ciao')
        self.coda.put({'timecode':tc, 'bufferone':self.bufferone})

    def start(self):
        osc_startup()
        # osc_startup(logger=logger)
        osc_udp_server("0.0.0.0", self.RECEIVING_PORT, "aggregatingServer")
        print(Fore.YELLOW + 'osc aggregator receiving on %s'%  self.RECEIVING_PORT)

        ###########################  single fella
        osc_method("/notch/drone*/X",   self.setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
        osc_method("/notch/drone*/Y",   self.setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
        osc_method("/notch/drone*/Z",   self.setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
        osc_method("/notch/drone*/R",   self.setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
        osc_method("/notch/drone*/G",   self.setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
        osc_method("/notch/drone*/B",   self.setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
        osc_method("/notch/timecode",   self.sendCompleteFrame, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
        def OSCLoop():
            # while not self.finished.is_set():
            while True:
                osc_process()
                time.sleep(self.oscProcessRate)
            osc_terminate()
            print('l\'aggregatore non ascolta più più')
        # Properly close the system.
        OSCLoopThread = threading.Thread(target=OSCLoop).start()
 
########## main
if __name__ == '__main__':
    print('se fossi main dovrei fare un sacco de roba')
