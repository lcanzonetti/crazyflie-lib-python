#rf 2021
import threading
import time
import repeatedTimer as rp

from   colorama              import Fore, Back, Style  
from   osc4py3.as_eventloop  import *
from   osc4py3               import oscmethod as osm
from   osc4py3               import oscbuildparse
from   random                import uniform


class Aggregator():
    def __init__(self, eventoFineDeMondo, coda, receivingPort, bufferone, oscProcessRate):
        self.RECEIVING_PORT   = receivingPort
        self.finished         = eventoFineDeMondo
        self.bufferone        = bufferone
        self.coda             = coda
        self.oscProcessRate   = oscProcessRate

    def setRequested(self, addr, val):
        print(addr, val)
        iddio     = int(addr[-3])
        value     = round(val,3)
        parametro = 'requested_' + addr[-1]
        setattr(self.bufferone[iddio], parametro, value)
    
    def sendCompleteFrame(self, addr, tc):
        self.coda.put([tc, self.bufferone])

    def start(self):
        osc_startup()
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
                osc_process()
                time.sleep(oscProcessRate)
            print('l\'aggregatore non ascolta più più')
        # Properly close the system.
        OSCLoopThread = threading.Thread(target=OSCLoop).start()
        osc_terminate()
 
########## main
if __name__ == '__main__':
    # print(bufferon)
    gino = Aggregator(bufferon)
    print(gino.bufferone)
    print('porco il clero')
 
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
