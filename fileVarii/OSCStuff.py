#rf 2021
import threading
import time
import repeatedTimer as rp

from   colorama             import Fore, Back, Style  
from   osc4py3.as_eventloop import *
from   osc4py3              import oscmethod as osm
from   osc4py3              import oscbuildparse
from   random               import uniform
import logging

OSC_IP           = "192.168.10.255"
COMPANION_IP     = "192.168.1.255"
SENDING_PORT     = 9201
RECEIVING_PORT   = 9200
COMPANION_PORT   = 12321
COMPANION_PAGE   = '93'
COMPANION_BUTTON = '10'

drogni        = {} 
bufferone     = {}
isSendEnabled = False
finished      = False

###########################  companion
def setSendEnabled (*args):
    global isSendEnabled
    isSendEnabled = not isSendEnabled
    print(Fore.RED +  'me dici: %s' % isSendEnabled)
    updateCompanion()
def getSendEnabled():
    return isSendEnabled
def comè(uno): # è booleano oppure no?
    uno = uno *1
    return uno
def updateCompanion():
    def daje ():
        while not finished:
            # print(Fore.WHITE +'aggiorno companion')
            if not isSendEnabled:
                col = oscbuildparse.OSCMessage("/style/bgcolor/"+COMPANION_PAGE+"/" + COMPANION_BUTTON, None,  [10, 235, 10])
                txt = oscbuildparse.OSCMessage("/style/text/"+COMPANION_PAGE+"/"    + COMPANION_BUTTON, None,   ["non mando"])
                bandoleon = oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, [col, txt]) 
                osc_send(bandoleon, "companionClient")

            else:
                col = oscbuildparse.OSCMessage("/style/bgcolor/"+COMPANION_PAGE+"/" + COMPANION_BUTTON, None,  [235, 10, 10])
                txt = oscbuildparse.OSCMessage("/style/text/"+COMPANION_PAGE+"/"    + COMPANION_BUTTON, None,   ["mando"])
                bandoleon = oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, [col, txt]) 
                osc_send(bandoleon, "companionClient")
            time.sleep(1)
    nnamo = threading.Thread(target=daje, daemon=True).start()

###########################  whole swarm
def takeoff(*args):
    # print(args)
    if isSendEnabled:
        print('chief says we\'re gonna take the fuck off')
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].takeoff(0.45, 2.45)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def go(unused_addr, args, isEnabled):
    if not isEnabled:
        print('chief says we\'re gonna do shit at sequence %s' % args)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].go(args)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def goLeft   (quanto):
    if isSendEnabled:
        print('chief says we\'re gonna go leftwards by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goLeft(quanto)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def goRight  (quanto):
    if isSendEnabled:
        print('chief says we\'re gonna go rightwards by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goRight(quanto)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def goForward(quanto):
    if isSendEnabled:
        print('chief says we\'re gonna go forward by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goForward(quanto)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def goBack   (quanto):
    if isSendEnabled:
        print('chief says we\'re gonna go back by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goBack(quanto)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def land     (*args):
    if isSendEnabled:
        print('chief says we\'re gotta be grounded')
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].land()
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def home     (unused_addr, args):
     if isSendEnabled:
        print('chief says we\'re gonna go home')
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goToHome()
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def ringColor(unused_addr, *args):
     if isSendEnabled:
        print('how fancy would it be to all look %s?' % [args] )
        # print (args[2])
        for drogno in drogni:
            drogni[drogno].setRingColor(args[1], args[2], args[3])
            # drogni[drogno].alternativeSetRingColor(args)
def kill     (unused_addr, *args):
     if isSendEnabled:
        print('everybody fuck now %s' % args )
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].killMeHardly()
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
                break
        finished = True

###########################  single fella
def printAndSendCoordinates():
    time.sleep(5)
    while not finished:
        time.sleep(0.5)
        for drogno in drogni:
            iddio = drogni[drogno].ID
            print ('il drone %s dovrebbe andare a %s %s %s' %( bufferone[iddio].name, bufferone[iddio].requested_X,bufferone[iddio].requested_Y,bufferone[iddio].requested_Z))
            if isSendEnabled and drogni[drogno].is_connected:
                 drogni[drogno].goTo(bufferone[iddio].requested_X, bufferone[iddio].requested_Y, bufferone[iddio].requested_Z)
                 drogni[drogno].setRingColor(bufferone[iddio].requested_R, bufferone[iddio].requested_G, bufferone[iddio].requested_B)
            else:
                # print('ma i comandi di movimento disabilitati')
                pass
 
def setRequested(*args):
    iddio     = int(args[0].split('/')[2][-1])
    parametro = args[0][-1]
    value     = round(args[1],3)

    # print (iddio, parametro, value)
    # try:
    if parametro == 'X' or parametro == 'Y':
        if value < -2:
            value = -2
        if value > 2:
            value = 2
    if parametro == 'Z':
        if value < 0.3:
            value = 0.30
    
    setattr(bufferone[iddio], parametro, value)
    # print('provo a variare il parametro %s mettendoci %s' % (parametro, value))
    # except:
    #     print('qualche porchiddio')

def start_server():          #### OSC init
    global finished 
    # logging.basicConfig(format='%(asctime)s - %(threadName)s ø %(name)s - ' '%(levelname)s - %(message)s')
    # logger = logging.getLogger("osc")
    # logger.setLevel(logging.DEBUG)
    # osc_startup(logger=logger)
    osc_startup()
    osc_udp_server("0.0.0.0", RECEIVING_PORT,             "receivingServer")
    osc_broadcast_client(OSC_IP,            SENDING_PORT,   "feedbackClient")
    osc_broadcast_client(COMPANION_IP,    COMPANION_PORT,   "companionClient")
    # osc_udp_client(OSC_IP,    SENDING_PORT,   "companionClient")

    print(Fore.GREEN + 'osc server initalized on',              RECEIVING_PORT, SENDING_PORT)
    print(Fore.GREEN + 'osc client to D3 initalized on',        OSC_IP, SENDING_PORT)
    print(Fore.GREEN + 'osc client to companion initalized on', OSC_IP, COMPANION_PORT)

    ###########################  single fella
    osc_method("/notch/drone*/X",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/notch/drone*/X",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/notch/drone*/Y",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/notch/drone*/Z",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/notch/drone*/R",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/notch/drone*/G",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/notch/drone*/B",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    ###########################  whole swarm routing
    osc_method("/takeoff",          takeoff, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/start",            go,      argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/land",             land,    argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/home",             home,    argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goLeft",           goLeft,  argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goRight",          goRight, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goForward",        goForward, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goBack",           goBack,    argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/ringColor",        ringColor, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/companion/isSendEnabled", setSendEnabled, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    updateCompanion()

    while not finished:
        osc_process()

        time.sleep(0.2)
    # Properly close the system.
    osc_terminate()

def faiIlBufferon():
    for i in range (1,20):
        bufferone[i] = bufferDrone(i)
    # print ('bufferon')  
    # print (bufferone)

# ################ feedbacksssssssss
def sendPose(droneID, x, y , z, yaw):
    ixxo = oscbuildparse.OSCMessage("/drogni/drone"+str(droneID)+"_pos_x", None, x)
    ypso = oscbuildparse.OSCMessage("/drogni/drone"+str(droneID)+"_pos_y", None, y)
    zeto = oscbuildparse.OSCMessage("/drogni/drone"+str(droneID)+"_pos_z", None, z)
    yalo = oscbuildparse.OSCMessage("/drogni/drone"+str(droneID)+"_rot_z", None, yaw)
    bun  = oscbuildparse.OSCBundle( oscbuildparse.OSC_IMMEDIATELY, [ixxo, ypso, zeto, yalo])  
    osc_send(bun, "feedbackClient")
    # print (droneID, roll, pitch, yaw)

########## main
if __name__ == '__main__':
    OSCRefreshThread      = threading.Thread(target=start_server,daemon=True).start()
    OSCPrintAndSendThread = threading.Thread(target=printAndSendCoordinates,daemon=True).start()
    sendPose(1,2,3,4,5)
    sendPose(1,2,3,4,5)
    sendPose(1,2,3,4,5)
    sendPose(1,2,3,4,5)
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
