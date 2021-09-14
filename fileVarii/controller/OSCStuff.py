# -*- coding: utf-8 -*-
#rf 2021
import threading
import multiprocessing
import time
from   colorama              import Fore, Back, Style
from   colorama              import init as coloInit  
# from   osc4py3.as_comthreads import *
from   osc4py3.as_eventloop  import *
from   osc4py3               import oscmethod as osm
from   osc4py3               import oscbuildparse
from   random                import random, uniform
import logging
import OSCaggregator

coloInit(convert=True)
FEEDBACK_IP             = "192.168.1.255"
FEEDBACK_PORT           = 9203

RECEIVING_IP            = "0.0.0.0"
RECEIVING_PORT          = 9200
OSC_PROCESS_RATE        = 0.001

COMPANION_IP            = "192.168.10.255"
COMPANION_PORT          = 12321
COMPANION_PAGES         = ['92', '93', '94']
TC_COMPANION_PAGE       = '91'
COMPANION_ENABLE_BUTTON = '25'
COMPANION_UPDATE_RATE   = 1
COMPANION_FEEDBACK_ENABLED = True

FEEDBACK_ENABLED        = False
FEEDBACK_RATE           = 0.8

COMMANDS_FREQUENCY      = 0.2

drogni        = {} 
bufferone     = {}
isSendEnabled = False
finished      = False
msgCount      = 0 
timecode      = '00:00:00:00'

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
    if COMPANION_FEEDBACK_ENABLED:
        for i in range(2,9):
            j=0
            for cp in COMPANION_PAGES:
                intst         = oscbuildparse.OSCMessage("/style/text/"+cp+"/"    + str(i),      None,   ['drone '+str(i-2+(j*7))])
                int_bkgcol    = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" + str(i),    ",iii",   [1, 1, 1])
                int_col       = oscbuildparse.OSCMessage("/style/color/"+cp+"/"   + str(i),    ",iii",   [60, 60, 60])

                status        = oscbuildparse.OSCMessage("/style/text/"+cp+"/"    + str(i+8),    None,   ['sconnesso'])
                status_bkgcol = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" + str(i+8),  ",iii",   [1, 1, 1])
                status_col    = oscbuildparse.OSCMessage("/style/color/"+cp+"/"   + str(i+8),  ",iii",   [120, 120, 120])

                tkfland       = oscbuildparse.OSCMessage("/style/text/"+cp+"/"    + str(i+16),   None,   ['take off'])
                tkfland_bkg   = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" + str(i+16), ",iii",   [60,  20,   1])
                tkfland_col   = oscbuildparse.OSCMessage("/style/color/"+cp+"/"   + str(i+16), ",iii",   [60, 60, 60])

                kill          = oscbuildparse.OSCMessage("/style/text/"+cp+"/"    + str(i+24),   None,   ['kill'])
                kill_bkg      = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" + str(i+24), ",iii",   [80, 10, 10])
                kill_col      = oscbuildparse.OSCMessage("/style/color/"+cp+"/"   + str(i+24), ",iii",   [60, 60, 60])

                bandoleon   = oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, [intst, int_bkgcol, int_col, status, status_bkgcol, status_col, tkfland, tkfland_bkg, tkfland_col, kill, kill_bkg, kill_col]) 
                osc_send(bandoleon, "companionClient")
                j+=1

def updateCompanion():
    global bufferone
    def daje ():
        while not finished:
            if COMPANION_FEEDBACK_ENABLED:
                time.sleep(COMPANION_UPDATE_RATE)
                # print(Fore.WHITE +'aggiorno companion')
                listaTimecode    = timecode.split(':')
                timecode_hours   = oscbuildparse.OSCMessage("/style/text/"+TC_COMPANION_PAGE+"/"    + str(29),   None,   [listaTimecode[0]])
                timecode_minutes = oscbuildparse.OSCMessage("/style/text/"+TC_COMPANION_PAGE+"/"    + str(30),   None,   [listaTimecode[1]])
                timecode_seconds = oscbuildparse.OSCMessage("/style/text/"+TC_COMPANION_PAGE+"/"    + str(31),   None,   [listaTimecode[2]])
                timecode_frames  = oscbuildparse.OSCMessage("/style/text/"+TC_COMPANION_PAGE+"/"    + str(32),   None,   [listaTimecode[3]])

                companionRate    = oscbuildparse.OSCMessage("/style/text/"+TC_COMPANION_PAGE+"/"    + str(24),   ",s",   ["Comp. Up. Rate" + str(COMPANION_UPDATE_RATE)])
                    
                    
                ticcio = oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, [  timecode_hours, timecode_minutes, timecode_seconds, timecode_frames, companionRate]) 
                osc_send(ticcio, "companionClient")
                
                if not isSendEnabled:                       #*******************  SEND ENABLING
                    for cp in COMPANION_PAGES:
                        col               = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" + COMPANION_ENABLE_BUTTON, None,  [10, 235, 10])
                        txt               = oscbuildparse.OSCMessage("/style/text/"+cp+"/"    + COMPANION_ENABLE_BUTTON, None,   ["non mando"])
                        col2              = oscbuildparse.OSCMessage("/style/bgcolor/90/21", None,  [10, 235, 10])
                        txt2              = oscbuildparse.OSCMessage("/style/text/90/21", None,   ["non mando"])
                        carlo = oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, [col, txt, col2, txt2 ]) 
                        osc_send(carlo, "companionClient")
                else:
                    for cp in COMPANION_PAGES:
                        col               = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" + COMPANION_ENABLE_BUTTON, None,  [235, 10, 10])
                        txt               = oscbuildparse.OSCMessage("/style/text/"+cp+"/"    + COMPANION_ENABLE_BUTTON, None,   ["mando"])
                        col2              = oscbuildparse.OSCMessage("/style/bgcolor/90/21", None,  [235, 10, 10])
                        txt2              = oscbuildparse.OSCMessage("/style/text/90/21"  , None,   ["mando"])
                        carlo = oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, [col, txt, col2, txt2 ]) 
                        osc_send(carlo, "companionClient")

                for drogno in drogni:               #*******************  singol-drogn               
                    cp   = COMPANION_PAGES[0]
                    iddio= drogni[drogno].ID
                    d    = drogni[drogno]   
                    if iddio>= 7 and iddio <14:
                        cp = int(cp)  + 1
                        iddio -= 7
                    if iddio >= 14:    
                        cp = int(cp)  + 2
                        iddio -= 14
                    cp = str(cp)
                    takeoffOrLand      = 'take off'
                    takeoffOrLandColor = [200,20,40]
                    if d.isReadyToFly:
                        takeoffOrLandColor = [20,200,40]
                    else:
                        takeoffOrLandColor = [100,90,40]

                    if d.isFlying:
                        takeoffOrLand = 'land'
                        if d.evaluateFlyness():  takeoffOrLandColor = [200,20,40]
                        else: takeoffOrLandColor = [255,0,0]

                    rgb = [bufferone[iddio].requested_R, bufferone[iddio].requested_G, bufferone[iddio].requested_B]
                    if not any(rgb): rgb = [40,40,40]

                    int_bkgcol    = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" + str(iddio+2),    ",iii", rgb )
                    int_col       = oscbuildparse.OSCMessage("/style/color/"+cp+"/"   + str(iddio+2),    ",iii",   [255,255,255])

                    status        = oscbuildparse.OSCMessage("/style/text/"+cp+"/"    + str(iddio+2+8),    ",s",   [d.statoDiVolo + ' ' + d.batteryVoltage]) 
                    status_bkgcol = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" + str(iddio+2+8),  ",iii",   [1, 1, 1])
                    status_col    = oscbuildparse.OSCMessage("/style/color/"+cp+"/"   + str(iddio+2+8),  ",iii",   [255, 255, 255])


                    tkfland       = oscbuildparse.OSCMessage("/style/text/"+cp+"/"    + str(iddio+2+16),   None,   [takeoffOrLand])
                    tkfland_bkg   = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" + str(iddio+2+16), ",iii",   takeoffOrLandColor)
                    tkfland_col   = oscbuildparse.OSCMessage("/style/color/"+cp+"/"   + str(iddio+2+16), ",iii",   [40, 40, 40])

                    kill          = oscbuildparse.OSCMessage("/style/text/"+cp+"/"    + str(iddio+2+24),   None,   [str(round(d.kalman_VarX,1)) + '' + str(round(d.kalman_VarY,1)) + ' ' + str(round(d.kalman_VarZ,1))])
                    kill_bkg      = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" + str(iddio+2+24), ",iii",   [55, 10, 10])
                    kill_col      = oscbuildparse.OSCMessage("/style/color/"+cp+"/"   + str(iddio+2+24), ",iii",   [255, 255, 255])

                    macron   = oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, [ int_bkgcol, int_col, status, status_bkgcol, status_col, tkfland, tkfland_bkg, tkfland_col, kill, kill_bkg, kill_col]) 
                    osc_send(macron, "companionClient")
 
    nnamo = threading.Thread(target=daje).start()

###########################  whole swarm
def takeOff(coddii, decollante):
    global bufferone
    def authorizedScrambleCommand():
        bufferone[drogni[drogno].ID].requested_X = drogni[drogno].x
        bufferone[drogni[drogno].ID].requested_Y = drogni[drogno].y
        try:
            gino = threading.Thread(target=drogni[drogno].takeoff).start()
            # drogni[drogno].takeoff(0.45, 2.45)
        except Exception:
            print('already taking off ? %s' % Exception)

    authorizedDrognos = 0
    if decollante == 'all':    # whole swarm logic
        print('chief says %s gonna take the fuck off' %(decollante))
        for drogno in drogni:
            if drogni[drogno].is_connected and drogni[drogno].evaluateFlyness():               
                authorizedDrognos += 1
                print(Fore.WHITE + 'Got %s drognos ready to scramble.' % authorizedDrognos)
                if authorizedDrognos == len(drogni):
                    print(Fore.GREEN + 'Got ENOUGH drognos ready to scramble!')
                    authorizedScrambleCommand()
            else:
                print('can\'t scramble drogno %s, not connected or not ready' % drogni[drogno].name)
    else:                         # single drogno logic, scramble or land
        if drogni[decollante].is_connected:
            if not drogni[decollante].isFlying:   # if it is not flying
                print('chief says %s gonna take the fuck off' %(decollante))
                if drogni[decollante].evaluateFlyness():  # and might fly
                    bufferone[drogni[decollante].ID].requested_X = drogni[decollante].x
                    bufferone[drogni[decollante].ID].requested_Y = drogni[decollante].y
                    try:
                        gino = threading.Thread(target=drogni[decollante].takeoff).start()
                        # drogni[decollante].takeoff(0.45, 2.45)
                    except Exception:
                        print('already taking off %s' % Exception)
                else: 
                    print('drone %s is not ready to fly' % drogni[decollante])
            else:            #if is flying already it may very well land
                print('chief says %s gonna land' %(decollante))
                drogni[decollante].land()
        else:
            print('il drogno %s non è connesso' % drogni[decollante].name)
def uploadSequence(coddii,quale):
        print('chief says we\'re gonna do shit at sequence %s' % quale)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].upload_trajectory(quale)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def startTest(coddii,quale):
        print('chief says we\'re gonna do testsss at sequence %s' % quale)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                print('cazzodio')
                drogni[drogno].startTest(quale, False)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def go       (coddii,quale):
        print('chief says we\'re gonna do shit at sequence %s' % quale)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].go(quale)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def goLeft   (coddii, quanto):
        print('chief says we\'re gonna go leftwards by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goLeft(quanto)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def goRight  (coddii, quanto):
        print('chief says we\'re gonna go rightwards by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goRight(quanto)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def goForward(coddii, quanto):
        print('chief says we\'re gonna go forward by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goForward(quanto)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def goBack   (coddii, quanto):
        print('chief says we\'re gonna go back by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goBack(quanto)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def land     (bullshit, landingCandidate):
    print('chief says %s gotta be grounded' % (landingCandidate))
    if landingCandidate == 'all':    
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].land()
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
    else:
        drogni[landingCandidate].land()
def home      (coddii, chi):
        print('chief says drogno_%s gonna go home' % chi)
        if drogni[chi].is_connected:
            if drogni[chi].isFlying:
                drogni[chi].goHome()
            else:
                print('il drogno %s non è connesso' % drogni[chi].name)
def goToStart (coddii, chi):
        print('chief says we (%s) are back at the start.' % chi)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goToStart(0.2)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def ringColor(*args):
    # print('how fancy would it be to all look %s %s %s ?' % (args[1][0], args[1][1], args[1][2]) )
    # print (bullshit)
    # print  (rgb[0])
    for drogno in drogni:
        if drogni[drogno].is_Connected:
            drogni[drogno].setRingColor(args[1][0], args[1][1], args[1][2])
        # drogni[drogno].alternativeSetRingColor(args)
def kill     (coddii, chi):
    print(' %s  fuck now' % chi )
    if chi == 'all':    
        for drogno in drogni:
            drogni[drogno].killMeHardly()
    else:
        drogni[chi].killMeSoftly()
def standBy  (coddii, chi):
    print(' %s  just go to sleep' % chi )
    if chi == 'all':    
        for drogno in drogni:
            drogni[drogno].goToSleep()
    else:
        drogni[chi].goToSleep()

###########################  single fella
def printAndSendCoordinates():
    global drogni
    global bufferone
    time.sleep(2)
    while not finished:
        time.sleep(COMMANDS_FREQUENCY)
        # if isSendEnabled:
        #     for drogno in drogni:
        #         iddio = drogni[drogno].ID
        if isSendEnabled:
            for drogno in drogni:
                iddio = drogni[drogno].ID
                if drogni[drogno].is_connected:
                    drogni[drogno].setRingColor(bufferone[iddio].requested_R, bufferone[iddio].requested_G, bufferone[iddio].requested_B)
                    # print ('il drone %s dovrebbe colorarsi a %s %s %s' %( bufferone[iddio].ID, bufferone[iddio].requested_R,bufferone[iddio].requested_G,bufferone[iddio].requested_B))
                    drogni[drogno].goTo(bufferone[iddio].requested_X, bufferone[iddio].requested_Y, bufferone[iddio].requested_Z)
                    # print ('il drone %s dovrebbe andare a %s %s %s' %( bufferone[iddio].name, bufferone[iddio].requested_X,bufferone[iddio].requested_Y,bufferone[iddio].requested_Z))
        # else:
        #     # print('ma i comandi di movimento disabilitati')
        #     pass
    print ('non potrò ricevere comandi di movimento, mai più')

def printHowManyMessages():
    def printa():
        while not finished:
            global msgCount
            time.sleep(5)
            if msgCount > 0.:
                print('\nho ricevuto %s messaggi OSC al secondo.' % str(msgCount/5))
            msgCount = 0
        print('D\'ora in poi la smetto di ricevere messaggi')

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
    global timecode
    msgCount += 1
    iddio      = int(address[-5])
    value1     = round(float(args[1]),3)
    value2     = round(float(args[2]),3)
    value3     = round(float(args[3]),3)
    timecode   = args[0]
    # print(timecode)
    # if isSendEnabled:
    # print('provo a variare il parametro posizione dell\'iddio %s mettendoci %s %s %s' % ( iddio, value1, value2, value3))
    bufferone[iddio].requested_X = value1
    bufferone[iddio].requested_Y = value2
    bufferone[iddio].requested_Z = value3
 
def setRequestedCol(address, args):
    global msgCount
    msgCount += 1
    iddio     = int(address[-7])
    bufferone[iddio].requested_R = int(args[1])
    bufferone[iddio].requested_G = int(args[2])
    bufferone[iddio].requested_B = int(args[3])

def setCompanionRate(address, args):
    global COMPANION_UPDATE_RATE
    if args[0] == '+':
        COMPANION_UPDATE_RATE += 0.1
    elif args[0] == '-':
        if COMPANION_UPDATE_RATE > 0:
            COMPANION_UPDATE_RATE -= 0.1
def setCommandsRate(address, args):
    global COMMANDS_FREQUENCY
    if args[0] == '+':
        COMMANDS_FREQUENCY += 0.1
    elif args[0] == '-':
        if COMMANDS_FREQUENCY > 0:
            COMMANDS_FREQUENCY -= 0.1


def start_server():          #### OSC init    #########    acts as main()
    global finished 
    global bufferone
    # logging.basicConfig(format='%(asctime)s - %(threadName)s ø %(name)s - ' '%(levelname)s - %(message)s')
    # logger = logging.getLogger("osc")
    # logger.setLevel(logging.DEBUG)
    # osc_startup(logger=logger)
    osc_startup( )
    osc_udp_server(RECEIVING_IP,             RECEIVING_PORT,   "receivingServer")
    if COMPANION_FEEDBACK_ENABLED:
        osc_broadcast_client(COMPANION_IP,    COMPANION_PORT,   "companionClient")
        print(Fore.GREEN + 'OSC client to companion initalized on', COMPANION_IP, COMPANION_PORT)

    if FEEDBACK_ENABLED:
        osc_broadcast_client(FEEDBACK_IP,   FEEDBACK_PORT,    "feedbackClient")
        print(Fore.GREEN + 'OSC feedback client initalized on',      FEEDBACK_IP, FEEDBACK_PORT)
        sendPose()

    print(Fore.GREEN + 'OSC server initalized on',              RECEIVING_IP, RECEIVING_PORT)

    ###########################  single fella
    osc_method("/notch/drone*/pos",   setRequestedPos, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)
    osc_method("/notch/drone*/color", setRequestedCol, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)
    ###########################  whole swarm routing
    osc_method("/takeOff",          takeOff,         argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/startTest",        startTest,       argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/upload",           uploadSequence,  argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/go",               go,              argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/land",             land,            argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/home",             home,            argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goToStart",        goToStart,       argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goLeft",           goLeft,          argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goRight",          goRight,         argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goForward",        goForward,       argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goBack",           goBack,          argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/kill",             kill,            argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/standBy",          standBy,         argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/ringColor",        ringColor,       argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)
    osc_method("/companion/isSendEnabled", setSendEnabled, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/setCompanionRate", setCompanionRate, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/setCommandsRate",  setCommandsRate, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)

    resetCompanion()
    updateCompanion()
    printHowManyMessages()

    while not finished:
        osc_process()
        time.sleep(OSC_PROCESS_RATE)
        # pass
    # Properly close the system.
    print('chiudo OSC')
    osc_terminate()

def faiIlBufferon():
    global bufferone
    for i in range (0,20):
        bufferone[i] = bufferDrone(i)
    # print ('bufferon')  
    # print (bufferone)
    # print(bufferone[0])

# ################ feedbacksssssssss
def sendPose():
    def treddo():
        while not finished:
            time.sleep(FEEDBACK_RATE)
            # for drogno in drogni:
            #     ixxo = oscbuildparse.OSCMessage("/drogni/drone"+str(drogni[drogno].ID)+"_pos_x", None,drogni[drogno].x)
            #     ypso = oscbuildparse.OSCMessage("/drogni/drone"+str(drogni[drogno].ID)+"_pos_y", None,drogni[drogno].y)
            #     zeto = oscbuildparse.OSCMessage("/drogni/drone"+str(drogni[drogno].ID)+"_pos_z", None,drogni[drogno].z)
            #     yalo = oscbuildparse.OSCMessage("/drogni/drone"+str(drogni[drogno].ID)+"_rot_z", None,drogni[drogno].yaw)
            ixxo = oscbuildparse.OSCMessage("/drogni/drone"+ str(random()),None,[random()])
            ypso = oscbuildparse.OSCMessage("/drogni/drone"+ str(random()),None,[random()])
            zeto = oscbuildparse.OSCMessage("/drogni/drone"+ str(random()),None,[random()])
            yalo = oscbuildparse.OSCMessage("/drogni/drone"+ str(random()),None,[random()])
            print("/drogni/drone"+ str(random()),None,random())
            bandoleon   = oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, [ ixxo, ypso, zeto, yalo]) 
            osc_send(bandoleon, "companionClient")
                # osc_process()
                # print (droneID, roll, pitch, yaw) 
        print(Fore.GREEN + 'closing feedback thread')
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
        self.requested_R            = 0
        self.requested_G            = 0
        self.requested_B            = 0
        self.yaw                   = 0.0


if __name__ == '__main__':
    faiIlBufferon()
    OSCRefreshThread      = threading.Thread(target=start_server).start()
    OSCPrintAndSendThread = threading.Thread(target=printAndSendCoordinates).start()
    # sendPose()
    while not finished:
        pass

# import keyboard

# while True:
#     keyboard.wait('q')
#     keyboard.send('ctrl+6')
 

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