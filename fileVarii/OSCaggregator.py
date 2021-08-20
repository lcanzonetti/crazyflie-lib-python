#rf 2021
import threading
import time
import repeatedTimer as rp

from   colorama              import Fore, Back, Style  
from   osc4py3.as_allthreads import *
from   osc4py3               import oscmethod as osm
from   osc4py3               import oscbuildparse
from   random                import uniform

OSC_IP           = "1127.0.0.1"
SENDING_PORT     = 9200
RECEIVING_PORT   = 9202
finished         = False
bufferone        = {}


def setRequested(*args):
    iddio     = int(args[0].split('/')[2][-1])
    parametro = args[0][-1]
    value     = round(args[1],3)
    parametro = 'requested_' + parametro
    setattr(bufferone[iddio], parametro, value)

def main():
    global finished 
    # logging.basicConfig(format='%(asctime)s - %(threadName)s ø %(name)s - ' '%(levelname)s - %(message)s')
    # logger = logging.getLogger("osc")
    # logger.setLevel(logging.DEBUG)
    # osc_startup(logger=logger)
    def faiIlBufferon():
        for i in range (0,20):
            bufferone[i] = bufferDrone(i)
    # print ('bufferon')  
    # print (bufferone)
    # print(bufferone[0])
    osc_startup(execthreadscount=20)
    osc_udp_server("0.0.0.0", RECEIVING_PORT,               "receivingServer")
    osc_broadcast_client(OSC_IP,            SENDING_PORT,    "feedbackClient")
    print(Fore.GREEN + 'osc aggegator initalized on',   RECEIVING_PORT, SENDING_PORT)

    ###########################  single fella
    osc_method("/notch/drone*/X",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/notch/drone*/Y",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/notch/drone*/Z",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/notch/drone*/R",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/notch/drone*/G",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/notch/drone*/B",   setRequested,  argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)

    while not finished:
        osc_process()
        time.sleep(0.1)
    # Properly close the system.
    osc_terminate()


########## main
if __name__ == '__main__':
    OSCRefreshThread      = threading.Thread(target=main,daemon=True).start()
    while not finished:
        pass

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
        self.yaw                   = 0.0
