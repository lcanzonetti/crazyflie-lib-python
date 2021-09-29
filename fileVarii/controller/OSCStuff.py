# -*- coding: utf-8 -*-
#rf 2021
import multiprocessing
import threading
from   threading import Lock
from   multiprocessing.connection import Client
from   multiprocessing.connection import Listener
from   multiprocessing import Process, Queue, Event
import queue
from   random                import random, uniform
import logging

import time

# from   osc4py3.as_comthreads import *
from   osc4py3.as_eventloop  import *
from   osc4py3               import oscmethod as osm
from   osc4py3               import oscbuildparse

from   colorama              import Fore, Back, Style
from   colorama              import init as coloInit  
coloInit(convert=True)

import OSCaggregator
import OSC_feedabcker as feedbacker

drogni        = {} 
bufferone     = {}
isSendEnabled = False
finished      = False
msgCount      = 0 
timecode      = '00:00:00:00'
framerate     = 25

################################################  this module osc receiving:
RECEIVING_IP            = "0.0.0.0"
RECEIVING_PORT          = 9200
OSC_PROCESS_RATE        = 0.001
################################################  notch osc aggregator:
AGGREGATION_ENABLED     = False
AGGREGATOR_RECEIVING_PORT = 9201
aggregatorInstance      = None
aggregatorProcess       = None
aggregatorCue           = Queue()
aggregatorExitEvent     = None
################################################  companion feedback via OSC:
COMPANION_FEEDBACK_SENDINGPORT = 12321
companionFeedbackCue    = Queue()  
COMPANION_FEEDBACK_IP   = None
COMPANION_PAGES         = ['92', '93', '94']
TC_COMPANION_PAGE       = '91'
COMPANION_ENABLE_BUTTON = '25'
COMPANION_UPDATE_RATE   = 0.6
COMPANION_FEEDBACK_ENABLED = True
##################################################  global rates:
commandsFrequency      = 0.15   # actual command'd rate to uavss
RECEIVED_MESSAGES_AVERAGE = 10
posLock = Lock()
# colLock = Lock()


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

                bandoleon   = [intst, int_bkgcol, int_col, status, status_bkgcol, status_col, tkfland, tkfland_bkg, tkfland_col, kill, kill_bkg, kill_col]
                companionFeedbackCue.put_nowait(bandoleon)
                j+=1

def updateCompanion():
    global bufferone
    # companionLock = Lock()
    def daje ():
        while not finished:
            if COMPANION_FEEDBACK_ENABLED:
                infinitaRoba = []
                time.sleep(COMPANION_UPDATE_RATE)
                # print(Fore.WHITE +'aggiorno companion')
                # companionLock.acquire()
                listaTimecode    = timecode.split(':')
                timecode_hours   = oscbuildparse.OSCMessage("/style/text/"+TC_COMPANION_PAGE+"/"    + str(29),   None,   [listaTimecode[0]])
                timecode_minutes = oscbuildparse.OSCMessage("/style/text/"+TC_COMPANION_PAGE+"/"    + str(30),   None,   [listaTimecode[1]])
                timecode_seconds = oscbuildparse.OSCMessage("/style/text/"+TC_COMPANION_PAGE+"/"    + str(31),   None,   [listaTimecode[2]])
                timecode_frames  = oscbuildparse.OSCMessage("/style/text/"+TC_COMPANION_PAGE+"/"    + str(32),   None,   [listaTimecode[3]])
                companionRate    = oscbuildparse.OSCMessage("/style/text/"+TC_COMPANION_PAGE+"/"    + str(11),   None,   [str(COMPANION_UPDATE_RATE)])
                commandsRate     = oscbuildparse.OSCMessage("/style/text/"+TC_COMPANION_PAGE+"/"    + str(13),   None,   [str(commandsFrequency)])
                # bandolone = oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, [  timecode_hours, timecode_minutes, timecode_seconds, timecode_frames, companionRate, commandsRate]) 
                infinitaRoba = [  timecode_hours, timecode_minutes, timecode_seconds, timecode_frames, companionRate, commandsRate]
                # osc_send(bandolone, "companionClient")
                
                if not isSendEnabled:                       #*******************  SEND ENABLING
                    for cp in COMPANION_PAGES:
                        col               = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" + COMPANION_ENABLE_BUTTON, None,  [10, 235, 10])
                        txt               = oscbuildparse.OSCMessage("/style/text/"+cp+"/"    + COMPANION_ENABLE_BUTTON, None,   ["non mando"])
                        col2              = oscbuildparse.OSCMessage("/style/bgcolor/90/21", None,   [10, 235, 10])
                        txt2              = oscbuildparse.OSCMessage("/style/text/90/21",    None,   ["non ricevo"])
                        infinitaRoba.extend( [col, txt, col2, txt2 ]) 
                        # carlo = oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, [col, txt, col2, txt2 ]) 
                        # osc_send(carlo, "companionClient")
                else:
                    for cp in COMPANION_PAGES:
                        col               = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" + COMPANION_ENABLE_BUTTON, None,  [235, 10, 10])
                        txt               = oscbuildparse.OSCMessage("/style/text/"+cp+"/"    + COMPANION_ENABLE_BUTTON, None,   ["mando"])
                        col2              = oscbuildparse.OSCMessage("/style/bgcolor/90/21", None,   [235, 10, 10])
                        txt2              = oscbuildparse.OSCMessage("/style/text/90/21"   , None,   ["ricevo"])
                        infinitaRoba.extend( [col, txt, col2, txt2 ]) 

                        # carlo = oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, [col, txt, col2, txt2 ]) 
                        # osc_send(carlo, "companionClient")

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
                    takeOffOrLand      = 'take off'
                    takeOffOrLandColor = [200,20,40]
                    if d.isReadyToFly:
                        takeOffOrLandColor = [20,200,40]
                    else:
                        takeOffOrLandColor = [100,90,40]

                    if d.isFlying:
                        takeOffOrLand = 'land'
                        if d.evaluateFlyness():  takeOffOrLandColor = [200,20,40]
                        else: takeOffOrLandColor = [255,0,0]

                    rgb = [bufferone[iddio].requested_R, bufferone[iddio].requested_G, bufferone[iddio].requested_B]
                    if not any(rgb) or d.standBy: rgb = [40,40,40]
                    if d.standBy: rgb = [40,100,40]

                    int_bkgcol    = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" + str(iddio+2),    ",iii", rgb )
                    int_col       = oscbuildparse.OSCMessage("/style/color/"+cp+"/"   + str(iddio+2),    ",iii",   [255,255,255])

                    status        = oscbuildparse.OSCMessage("/style/text/"+cp+"/"    + str(iddio+2+8),    ",s",   [d.statoDiVolo + ' ' + d.batteryVoltage]) 
                    status_bkgcol = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" + str(iddio+2+8),  ",iii",   [1, 1, 1])
                    status_col    = oscbuildparse.OSCMessage("/style/color/"+cp+"/"   + str(iddio+2+8),  ",iii",   [255, 255, 255])

                    tkfland       = oscbuildparse.OSCMessage("/style/text/"+cp+"/"    + str(iddio+2+16),   None,   [takeOffOrLand])
                    tkfland_bkg   = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" + str(iddio+2+16), ",iii",   takeOffOrLandColor)
                    tkfland_col   = oscbuildparse.OSCMessage("/style/color/"+cp+"/"   + str(iddio+2+16), ",iii",   [40, 40, 40])

                    kill          = oscbuildparse.OSCMessage("/style/text/"+cp+"/"    + str(iddio+2+24),   None,   [str(round(d.kalman_VarX,1)) + '' + str(round(d.kalman_VarY,1)) + ' ' + str(round(d.kalman_VarZ,1))])
                    kill_bkg      = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" + str(iddio+2+24), ",iii",   [55, 10, 10])
                    kill_col      = oscbuildparse.OSCMessage("/style/color/"+cp+"/"   + str(iddio+2+24), ",iii",   [255, 255, 255])

                    infinitaRoba.extend([ int_bkgcol, int_col, status, status_bkgcol, status_col, tkfland, tkfland_bkg, tkfland_col, kill, kill_bkg, kill_col]) 
                    companionFeedbackCue.put_nowait(infinitaRoba)
                    # companionLock.release()
    nnamo = threading.Thread(target=daje).start()

###########################  whole swarm
def takeOff(coddii, decollante):
    global bufferone
    # safeLocckino = Lock()
    def authorizedScrambleCommand():
        # safeLocckino.acquire()
        for drogno in drogni:
            bufferone[drogni[drogno].ID].requested_X = drogni[drogno].x
            bufferone[drogni[drogno].ID].requested_Y = drogni[drogno].y
            drogni[drogno].takeOff()
        # safeLocckino.release()

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
                print('chief says %s gonna take the fuck off' %(drogni[decollante]))
                if drogni[decollante].evaluateFlyness():  # and might fly
                    bufferone[drogni[decollante].ID].requested_X = drogni[decollante].x
                    bufferone[drogni[decollante].ID].requested_Y = drogni[decollante].y
                    try:
                        gino = threading.Thread(target=drogni[decollante].takeOff).start()
                        # drogni[decollante].takeOff(0.45, 2.45)
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
        print('chief says we\'re upload shit at sequence %s' % quale)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].upload_trajectory(quale)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def startTest (coddii,quale):
        print('chief says we\'re gonna do testsss at sequence %s' % quale)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                print('cazzodio')
                drogni[drogno].startTest(quale, False)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def go        (coddii,quale):
        print('chief says we\'re gonna do shit at sequence %s' % quale)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].go(quale)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def goLeft    (coddii, quanto):
        print('chief says we\'re gonna go leftwards by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goLeft(quanto)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def goRight   (coddii, quanto):
        print('chief says we\'re gonna go rightwards by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goRight(quanto)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def goForward (coddii, quanto):
        print('chief says we\'re gonna go forward by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goForward(quanto)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def goBack    (coddii, quanto):
        print('chief says we\'re gonna go back by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goBack(quanto)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def land      (bullshit, landingCandidate):
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
def ringColor (*args):
    # print('how fancy would it be to all look %s %s %s ?' % (args[1][0], args[1][1], args[1][2]) )
    # print (bullshit)
    # print  (rgb[0])
    for drogno in drogni:
        if drogni[drogno].is_Connected:
            drogni[drogno].setRingColor(args[1][0], args[1][1], args[1][2])
        # drogni[drogno].alternativeSetRingColor(args)
def kill      (coddii, chi):
    print(' %s  fuck now' % chi )
    if chi == 'all':    
        for drogno in drogni:
            drogni[drogno].killMeHardly()
    else:
        drogni[chi].killMeHardly()
def standBy   (coddii, chi):
    print(' %s  just go to sleep' % chi )
    if chi == 'all':    
        for drogno in drogni:
            drogni[drogno].goToSleep()
    else:
        if not drogni[int(chi)].standBy:
            drogni[int(chi)].goToSleep()
        else:
            drogni[int(chi)].wakeUp()
def wakeUp    (coddii, chi):
    print(' %s  wakeUp' % chi )
    if chi == 'all':    
        for drogno in drogni:
            drogni[drogno].wakeUp()
    else:
        drogni[chi].wakeUp()
def resetEstimator  (coddii, chi):
    print(' %s  resetEstimator' % chi )
    if chi == 'all':    
        for drogno in drogni:
            drogni[drogno].resetEstimator()
    else:
        drogni[chi].resetEstimator()

###########################  single fella
def printAndSendCoordinates():
    global drogni
    global bufferone
    # time.sleep(2)
    while not finished:
        time.sleep(commandsFrequency)
        # if isSendEnabled:
        #     for drogno in drogni:
        #         iddio = drogni[drogno].ID
        if isSendEnabled:
            for drogno in drogni:
                iddio = drogni[drogno].ID
                if drogni[drogno].is_connected:
                    # with colLock:
                        drogni[drogno].setRingColor(bufferone[iddio].requested_R, bufferone[iddio].requested_G, bufferone[iddio].requested_B)
                    # print ('il drone %s dovrebbe colorarsi a %s %s %s' %( bufferone[iddio].ID, bufferone[iddio].requested_R,bufferone[iddio].requested_G,bufferone[iddio].requested_B))
                    # with posLock:
                        drogni[drogno].goTo(bufferone[iddio].requested_X, bufferone[iddio].requested_Y, bufferone[iddio].requested_Z)
                    # print ('il drone %s dovrebbe andare a %s %s %s' %( bufferone[iddio].name, bufferone[iddio].requested_X,bufferone[iddio].requested_Y,bufferone[iddio].requested_Z))
        # else:
        #     # print('ma i comandi di movimento disabilitati')
        #     pass
    print ('Non potrò mai più inviare ai drogni comandi di movimento, mai più')

def printHowManyMessages():
    # howManyMessagesLock = Lock()
    def printa():
        while not finished:
            global msgCount
            time.sleep(RECEIVED_MESSAGES_AVERAGE)
            # with howManyMessagesLock:
            if msgCount > 0.:
                print('\nNegli ultimi %s secondi ho ricevuto la media di %s messaggi OSC al secondo.' % (RECEIVED_MESSAGES_AVERAGE ,str(msgCount/RECEIVED_MESSAGES_AVERAGE)))
            msgCount = 0
        print('D\'ora in poi la smetto di ricevere messaggi')

    threading.Thread(target=printa).start()

def setRequestedPos(address, args):
    global msgCount
    global timecode
    iddio      = int(address[-5])
        # print(timecode)
        # if isSendEnabled:
        # print('provo a variare il parametro posizione dell\'iddio %s mettendoci %s %s %s' % ( iddio, value1, value2, value3))
    with posLock: 
        timecode   = args[0]
        bufferone[iddio].requested_X = round(float(args[1]),3)
        bufferone[iddio].requested_Y = round(float(args[2]),3)
        bufferone[iddio].requested_Z = round(float(args[3]),3)
        msgCount += 1

def setRequestedCol(address, args):
    global msgCount
    iddio     = int(address[-7])
    # with colLock:
    msgCount += 1
    bufferone[iddio].requested_R = args[1]
    bufferone[iddio].requested_G = args[2]
    bufferone[iddio].requested_B = args[3]

def setCompanionRate(address, args):
    global COMPANION_UPDATE_RATE
    # print(args)
    if args[0] == '+':
        COMPANION_UPDATE_RATE += 0.1
    elif args[0] == '-':
        if COMPANION_UPDATE_RATE > 0:
            COMPANION_UPDATE_RATE -= 0.1
    COMPANION_UPDATE_RATE = round(COMPANION_UPDATE_RATE, 2)
    print(COMPANION_UPDATE_RATE)
    
def setCommandsRate(address, args):
    global commandsFrequency
    # print(args)
    if args[0] == '+':
        commandsFrequency += 0.05
    elif args[0] == '-':
        if commandsFrequency > 0:
            commandsFrequency -= 0.05
    commandsFrequency = round(commandsFrequency, 2)
    for drogno in drogni:
        drogni[drogno].commandsFrequency = commandsFrequency
    
    print(Fore.RED + 'commandsFrequency has been set to ' + str(commandsFrequency))

def start_server():      ######################    #### OSC init    #########    acts as main()
    global finished 
    global bufferone
    global timecode
    # logging.basicConfig(format='%(asctime)s - %(threadName)s ø %(name)s - ' '%(levelname)s - %(message)s')
    # logger = logging.getLogger("osc")
    # logger.setLevel(logging.DEBUG)
    # osc_startup(logger=logger)
    osc_startup()
    osc_udp_server(RECEIVING_IP,             RECEIVING_PORT,   "receivingServer")
    print(Fore.GREEN + 'OSC receiving server initalized on',   RECEIVING_IP, RECEIVING_PORT)
    # print ('ma porco il clero di ' + COMPANION_FEEDBACK_IP)
    
    if COMPANION_FEEDBACK_ENABLED:
        companionFeedbackerInstance = feedbacker.CompanionFeedbacco( companionFeedbackCue, COMPANION_FEEDBACK_IP, COMPANION_FEEDBACK_SENDINGPORT)
        companionFeedbackProcess = Process(target=companionFeedbackerInstance.start)
        companionFeedbackProcess.daemon = True
        companionFeedbackProcess.start() 
   
    if AGGREGATION_ENABLED:
        global aggregatorInstance
        global aggregatorProcess
        aggregatorInstance = OSCaggregator.Aggregator(aggregatorExitEvent, aggregatorCue, AGGREGATOR_RECEIVING_PORT, bufferone, OSC_PROCESS_RATE, framerate )
        aggregatorProcess  = Process(target=aggregatorInstance.start)
        aggregatorProcess.daemon = True
        aggregatorProcess.start() 
    
    ###########################  single fella requested position
    osc_method("/notch/drone*/pos",   setRequestedPos, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)
    osc_method("/notch/drone*/color", setRequestedCol, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)
    ###########################  swarm or single commnands
    osc_method("/takeOff",          takeOff,         argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/startTest",        startTest,       argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/upload",           uploadSequence,  argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    # osc_method("/go",               go,              argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/land",             land,            argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/home",             home,            argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goToStart",        goToStart,       argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goLeft",           goLeft,          argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goRight",          goRight,         argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goForward",        goForward,       argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goBack",           goBack,          argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/kill",             kill,            argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/standBy",          standBy,         argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/wakeUp",           wakeUp,          argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/resetEstimator",   resetEstimator,  argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)


    osc_method("/ringColor",        ringColor,       argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)
    osc_method("/companion/isSendEnabled", setSendEnabled, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/setCompanionRate", setCompanionRate, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/setCommandsRate",  setCommandsRate, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    ############################################################
    resetCompanion()
    updateCompanion()
    printHowManyMessages()

    # aggregationLock = Lock()
    while not finished:
        time.sleep(OSC_PROCESS_RATE)
        osc_process()
        if AGGREGATION_ENABLED:
            global timecode
            try:
                roba = aggregatorCue.get(block=False)
                # aggregatorCue.task_done()
                # with aggregationLock:             
                timecode  = roba['timecode']
                bufferone = roba['bufferone']
                print('ricevuto questo timecode dall\'aggregatore: %s' %timecode)
            except  (queue.Empty, AttributeError):
                pass
    # Properly close the system.
    print('chiudo OSC')
    companionFeedbackCue.put('fuck you')
    aggregatorExitEvent.set()
    # aggregatorProcess.join()
    osc_terminate()

def faiIlBufferon():
    global bufferone
    for i in range (0,20):
        bufferone[i] = bufferDrone(i)

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
    COMPANION_FEEDBACK_IP = "192.168.1.255"
    OSCRefreshThread      = threading.Thread(target=start_server).start()
    OSCPrintAndSendThread = threading.Thread(name='printAndSendThread', target=printAndSendCoordinates).start()
    # sendPose()
    while not finished:
        pass
 
    # logging.basicConfig(format='%(asctime)s - %(threadName)s ø %(name)s - ' '%(levelname)s - %(message)s')
    # logger = logging.getLogger("osc")
    # logger.setLevel(logging.DEBUG)
    # osc_startup(logger=logger)