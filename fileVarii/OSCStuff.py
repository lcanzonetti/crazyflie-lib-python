# -*- coding: utf-8 -*-
#rf 2021
import threading
import multiprocessing
import time
import repeatedTimer as rp
from   colorama              import Fore, Back, Style
from   colorama              import init as coloInit  
# from   osc4py3.as_comthreads import *
from   osc4py3.as_eventloop  import *
from   osc4py3               import oscmethod as osm
from   osc4py3               import oscbuildparse
from   random                import uniform
import logging

# import OSCaggregator
coloInit(convert=True)
OSC_IP                  = "192.168.10.255"
RECEIVING_IP            = "0.0.0.0"
SENDING_PORT            = 9201
RECEIVING_PORT          = 9200
OSC_PROCESS_RATE        = 0.01

COMPANION_IP            = "192.168.10.255"
COMPANION_PORT          = 12321
COMPANION_PAGE          = '92'
COMPANION_ENABLE_BUTTON = '25'
COMPANION_UPDATE_RATE   = 0.8

FEEDBACK_ENABLED        = True
FEEDBACK_RATE           = 0.8

drogni        = {} 
bufferone     = {}
isSendEnabled = False
finished      = False

msgCount =0 

###########################  companion
def setSendEnabled (*args):
    global isSendEnabled
    isSendEnabled = not isSendEnabled
    print(Fore.RED +  'me dici: %s' % isSendEnabled)
    
def getSendEnabled():
    return isSendEnabled
def comè(uno): # è booleano oppure no?
    uno = uno *1
    return uno

def resetCompanion():
    for i in range(2,9):
        active_col = oscbuildparse.OSCMessage("/style/bgcolor/"+COMPANION_PAGE+"/" + str(i),  ",iii",   [1, 80, 1])
        carlo      = oscbuildparse.OSCMessage("/style/text/"+COMPANION_PAGE+"/" + str(i),   None,   ['drone '+str(i-2)])
        pino       = oscbuildparse.OSCMessage("/style/color/"+COMPANION_PAGE+"/" + str(i),  ",iii",   [255, 255, 255])
        bandoleon = oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, [active_col, carlo, pino]) 
        osc_send(bandoleon, "companionClient")


def updateCompanion():
    def daje ():
        while not finished:
            # print(Fore.WHITE +'aggiorno companion')
            if not isSendEnabled:
                col = oscbuildparse.OSCMessage("/style/bgcolor/"+COMPANION_PAGE+"/" + COMPANION_ENABLE_BUTTON, None,  [10, 235, 10])
                txt = oscbuildparse.OSCMessage("/style/text/"+COMPANION_PAGE+"/"    + COMPANION_ENABLE_BUTTON, None,   ["non mando"])
                bandoleon = oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, [col, txt]) 
                osc_send(bandoleon, "companionClient")
            else:
                col = oscbuildparse.OSCMessage("/style/bgcolor/"+COMPANION_PAGE+"/" + COMPANION_ENABLE_BUTTON, None,  [235, 10, 10])
                txt = oscbuildparse.OSCMessage("/style/text/"+COMPANION_PAGE+"/"    + COMPANION_ENABLE_BUTTON, None,   ["mando"])
                bandoleon = oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, [col, txt]) 
                osc_send(bandoleon, "companionClient")
            for drogno in drogni:
                d = drogni[drogno]
                active_col = oscbuildparse.OSCMessage("/style/bgcolor/"+COMPANION_PAGE+"/" + str(d.ID+2),   None,   [13, 244, 244])
                txt        = oscbuildparse.OSCMessage("/style/text/"+COMPANION_PAGE+"/"    + str(d.ID+2+8), None,   [d.statoDiVolo])
                scrambleCol = ''
                scrambleTxt = ''
                if d.isFlying:
                    scrambleCol = oscbuildparse.OSCMessage("/style/bgcolor/"+COMPANION_PAGE+"/" + str(d.ID+2+8+8),   None,   [244, 136, 8])
                    scrambleTxt = oscbuildparse.OSCMessage("/style/txt/"+COMPANION_PAGE+"/" + str(d.ID+2+8+8),   None,   ['land ' + str(d.batteryVoltage)])
                else:
                    scrambleCol = oscbuildparse.OSCMessage("/style/bgcolor/"+COMPANION_PAGE+"/" + str(d.ID+2+8+8),   None,   [50, 127, 67])
                    scrambleTxt = oscbuildparse.OSCMessage("/style/txt/"+COMPANION_PAGE+"/" + str(d.ID+2+8+8),   None,   ['take off ' + str(d.batteryVoltage)])

    
                bandoleon = oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, [active_col, txt, scrambleTxt, scrambleCol])
                osc_send(bandoleon, "companionClient")

            time.sleep(COMPANION_UPDATE_RATE)
    nnamo = threading.Thread(target=daje).start()

###########################  whole swarm
def takeoff(*args):
    global bufferone
    print('chief says we\'re gonna take the fuck off')
    for drogno in drogni:
        if drogni[drogno].is_connected:
            bufferone[drogni[drogno].ID].requested_X = drogni[drogno].x
            bufferone[drogni[drogno].ID].requested_Y = drogni[drogno].y
            drogni[drogno].takeoff(0.45, 2.45)
        else:
            print('il drogno %s non è connesso' % drogni[drogno].name)
def go(unused_addr, args, isEnabled):
        print('chief says we\'re gonna do shit at sequence %s' % args)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].go(args)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def goLeft   (quanto):
        print('chief says we\'re gonna go leftwards by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goLeft(quanto)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def goRight  (quanto):
        print('chief says we\'re gonna go rightwards by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goRight(quanto)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def goForward(quanto):
        print('chief says we\'re gonna go forward by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goForward(quanto)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def goBack   (quanto):
        print('chief says we\'re gonna go back by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goBack(quanto)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def land     (*args):
    print('chief says we\'re gotta be grounded')
    for drogno in drogni:
        if drogni[drogno].is_connected:
            drogni[drogno].land()
        else:
            print('il drogno %s non è connesso' % drogni[drogno].name)
def home     (unused_addr, args):
        print('chief says we\'re gonna go home')
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goToHome()
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def ringColor(unused_addr, *args):
        print('how fancy would it be to all look %s?' % [args] )
        # print (args[2])
        for drogno in drogni:
            drogni[drogno].setRingColor(args[1], args[2], args[3])
            # drogni[drogno].alternativeSetRingColor(args)
def kill     (unused_addr, *args):
        print('everybody fuck now %s' % args )
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].killMeHardly()
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
                break
        # finished = True

###########################  single fella
def printAndSendCoordinates():
    global drogni
    global bufferone
    # print(bufferone)
    time.sleep(1)
    while not finished:
        time.sleep(0.4)
        # print ('tipo: ', str(bufferone[0].requested_X))
        # print ('tipo: ', str(bufferone[1].requested_X))
        # print ('tipo: ', str(bufferone[2].requested_X))
        # print ('tipo: ', str(bufferone[3].requested_X))
        # print ('tipo: ', str(bufferone[4].requested_X))
        # print ('tipo: ', str(bufferone[5].requested_X))
        # print ('tipo: ', str(bufferone[6].requested_X))
        # print ('tipo: ', str(bufferone[7].requested_X))
        # print ('tipo: ', str(bufferone[8].requested_X))
        if isSendEnabled:
            for drogno in drogni:
                iddio = drogni[drogno].ID
                # print ('il drone %s dovrebbe colorarsi a %s %s %s' %( bufferone[iddio].name, bufferone[iddio].requested_R,bufferone[iddio].requested_G,bufferone[iddio].requested_B))
                if drogni[drogno].is_connected:
                    # drogni[drogno].setRingColor(bufferone[iddio].requested_R, bufferone[iddio].requested_G, bufferone[iddio].requested_B)
                    if  drogni[drogno].isFlying:
                        drogni[drogno].goTo(bufferone[iddio].requested_X, bufferone[iddio].requested_Y, bufferone[iddio].requested_Z)
                        # print ('il drone %s dovrebbe andare a %s %s %s' %( bufferone[iddio].name, bufferone[iddio].requested_X,bufferone[iddio].requested_Y,bufferone[iddio].requested_Z))
        # else:
        #     # print('ma i comandi di movimento disabilitati')
        #     pass

def printHowManyMessages():
    def printa():
        while not finished:
            time.sleep(1)
            global msgCount
            time.sleep(1)
            print('ho ricevuto %s messaggi.' % msgCount)
            msgCount = 0

    threading.Thread(target=printa).start()

def setRequested(*args):
    iddio     = int(args[0].split('/')[2][-1])
    parametro = args[0][-1]
    value     = round(args[1],3)
    parametro = 'requested_' + parametro
   
    setattr(bufferone[iddio], parametro, value)
    # print('provo a variare il parametro %s mettendoci %s' % (parametro, value))

def setRequestedPos(address, args):
    global msgCount
    msgCount += 1
    iddio      = int(address[-5])
    value1     = round(float(args[0]),3)
    value2     = round(float(args[1]),3)
    value3     = round(float(args[2]),3)
    # if isSendEnabled:
    # print('provo a variare il parametro posizione dell\'iddio %s mettendoci %s %s %s' % ( iddio, value1, value2, value3))
    bufferone[iddio].requested_X = value1
    bufferone[iddio].requested_Y = value2
    bufferone[iddio].requested_Z = value3
 
def setRequestedCol(address, args):
    iddio     = int(address[-5])
    global msgCount
    msgCount += 1
    # value1     = round(float(add[1]),3)
    # value2     = round(float(add[2]),3)
    # value3     = round(float(add[3]),3)
    # if isSendEnabled:
    print('provo a variare il parametro del drone %s colore mettendoci %s %s %s' % ( iddio, args[1], args[2], args[3]))

    bufferone[iddio].requested_R = int(args[1])
    bufferone[iddio].requested_G = int(args[2])
    bufferone[iddio].requested_B = int(args[3])
    # setattr(bufferone[iddio], parametro, value)

def start_server():          #### OSC init    #########    acts as main()
    global finished 
    global bufferone
    # with multiprocessing.Manager() as manager:
    # if True:

    # logging.basicConfig(format='%(asctime)s - %(threadName)s ø %(name)s - ' '%(levelname)s - %(message)s')
    # logger = logging.getLogger("osc")
    # logger.setLevel(logging.DEBUG)
    # osc_startup(logger=logger)
    osc_startup( )
    osc_udp_server(RECEIVING_IP,             RECEIVING_PORT,   "receivingServer")
    osc_broadcast_client(COMPANION_IP,    COMPANION_PORT,   "companionClient")
    if FEEDBACK_ENABLED:
        osc_broadcast_client(OSC_IP,            SENDING_PORT,    "feedbackClient")
        sendPose()

     # aggregoneThread  = threading.Thread(target=aggregatore.main, args=(bufferone,))
    # aggregoneThread.start()
    # sharedBuffer = manager.dict()
    # sharedBuffer = bufferone
    # print('sharedBuffer:  ')
    # print(sharedBuffer)
    # aggregatore      = OSCaggregator.Aggregator()
    # aggregoneThread  = multiprocessing.Process(target=aggregatore.main, args=(sharedBuffer,))
    # aggregoneThread  = threading.Thread(target=aggregatore.main, args=(bufferone,))
    # aggregoneThread.start()
    # print('sharedBuffer after:  ')
    # print(sharedBuffer)
    
    # aggregoneThread.join()

    print(Fore.GREEN + 'osc server initalized on',              RECEIVING_IP, RECEIVING_PORT)
    print(Fore.GREEN + 'osc feedback client initalized on',        OSC_IP, SENDING_PORT)
    print(Fore.GREEN + 'osc client to companion initalized on', COMPANION_IP, COMPANION_PORT)

    ###########################  single fella
    # osc_method("/notch/drone*/X",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    # osc_method("/notch/drone*/Y",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    # osc_method("/notch/drone*/Z",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    # osc_method("/notch/drone*/R",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    # osc_method("/notch/drone*/G",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    # osc_method("/notch/drone*/B",   setRequested,    argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/notch/drone*/pos", setRequestedPos, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)
    osc_method("/notch/drone*/col", setRequestedCol, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)
    ###########################  whole swarm routing
    osc_method("/takeoff",          takeoff,   argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/start",            go,        argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/land",             land,      argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/home",             home,      argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goLeft",           goLeft,    argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goRight",          goRight,   argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goForward",        goForward, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goBack",           goBack,    argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/kill",             kill,    argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/ringColor",        ringColor, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/companion/isSendEnabled", setSendEnabled, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    resetCompanion()
    updateCompanion()
    printHowManyMessages()

    while not finished:
        osc_process()
        time.sleep(OSC_PROCESS_RATE)
        # pass
    # Properly close the system.
    osc_terminate()

def faiIlBufferon():
    global bufferone
    for i in range (0,9):
        bufferone[i] = bufferDrone(i)
    # print ('bufferon')  
    # print (bufferone)
    # print(bufferone[0])

# ################ feedbacksssssssss
def sendPose():
    def treddo():
        time.sleep(FEEDBACK_RATE)
        for drogno in drogni:
            ixxo = oscbuildparse.OSCMessage("/drogni/drone"+str(drogni[drogno].ID)+"_pos_x", None,drogni[drogno].x)
            ypso = oscbuildparse.OSCMessage("/drogni/drone"+str(drogni[drogno].ID)+"_pos_y", None,drogni[drogno].y)
            zeto = oscbuildparse.OSCMessage("/drogni/drone"+str(drogni[drogno].ID)+"_pos_z", None,drogni[drogno].z)
            yalo = oscbuildparse.OSCMessage("/drogni/drone"+str(drogni[drogno].ID)+"_rot_z", None,drogni[drogno].yaw)
            bun  = oscbuildparse.OSCBundle( oscbuildparse.OSC_IMMEDIATELY, [ixxo, ypso, zeto, yalo])  
            osc_send(bun, "feedbackClient")
            # print (droneID, roll, pitch, yaw) 
    print(Fore.GREEN + 'starting feedback thread')
    feedbackTreddo = threading.Thread(target=treddo).start()


########## main
class bufferDrone():
    def __init__(self, ID, ):
        self.ID          = int(ID)
        self.name        = 'bufferDrone'+str(ID)
        
        self.requested_X            = 0.0
        self.requested_Y            = 0.0
        self.requested_Z            = 1.0
        self.requested_R            = 0.0
        self.requested_G            = 0.0
        self.requested_B            = 0.0
        self.yaw                   = 0.0


if __name__ == '__main__':
    faiIlBufferon()
    OSCRefreshThread      = threading.Thread(target=start_server,daemon=True).start()
    OSCPrintAndSendThread = threading.Thread(target=printAndSendCoordinates,daemon=True).start()

    while not finished:
        pass

# import keyboard

# while True:
#     keyboard.wait('q')
#     keyboard.send('ctrl+6')
 

