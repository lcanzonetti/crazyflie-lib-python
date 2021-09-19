#rf 2021
import threading
import time 
from   multiprocessing import Process, Queue, Event

from   colorama              import Fore, Back, Style
from   colorama              import init as coloInit  
coloInit(convert=True)

import pytimecode as ptc


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
    def __init__(self, eventoFineDeMondo, coda, receivingPort, bufferone, oscProcessRate, framerate):
        self.RECEIVING_PORT   = receivingPort
        self.finished         = eventoFineDeMondo
        self.bufferone        = bufferone
        self.coda             = coda
        self.oscProcessRate   = oscProcessRate
        self.framerate        = framerate
        self.pytc             = ptc.PyTimeCode(self.framerate)

    def setRequested(self, addr, val):
        # print(addr, val)
        iddio     = int(addr[-3])
        value     = round(val,3)
        parametro = 'requested_' + addr[-1]
        setattr(self.bufferone[iddio], parametro, value)
    
    def sendCompleteFrame(self, addr, tc):
        # self.coda.put('ciao')
        frames = int(tc/self.framerate)
        hrs    = int(frames/(3600*self.framerate))
        #check to see if hours => 24. SMPTE Timecode only goes to 24 hours
        if hrs > 23:
            hrs = hrs % 24
            frames = frames - (24 * 3600 * self.framerate)
        mins = int((frames%(3600*self.framerate))/(60*self.framerate))
        secs = int(((frames%(3600*self.framerate))%(60*self.framerate))/self.framerate)
        frs =  int(((frames%(3600*self.framerate))%(60*self.framerate))%self.framerate)
        timecodeBello = str(hrs).zfill(2)+":"+str(mins).zfill(2)+":"+str(secs).zfill(2)+":"+str(frs).zfill(2)
        self.coda.put({'timecode':timecodeBello, 'bufferone':self.bufferone})
        # print('timecodebello: %s' % timecodeBello)

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
            while not self.finished.is_set():
            # while True:
                osc_process()
                time.sleep(0.04)
            osc_terminate()
            print('l\'aggregatore non ascolta più più')
        # Properly close the system.
        OSCLoopThread = threading.Thread(target=OSCLoop).start()
 
########## main
if __name__ == '__main__':
    print('se fossi main dovrei fare un sacco de roba')
