# -*- coding: utf-8 -*-
#rf 2021
from OSC_feedabcker import CompanionFeedbacco
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
from   osc4py3.as_eventloop  import *
from   osc4py3               import oscmethod as osm
from   osc4py3               import oscbuildparse

# from   main                  import WE_ARE_FAKING_IT

from   colorama              import Fore, Back, Style
from   colorama              import init as coloInit  
coloInit(convert=True)

import OSCaggregator
from GUI import setCompanionRate, setFlyability, set_command_frequency,weMaySend


drogni        = {} 
bufferone     = {}
isSendEnabled = False
isSwarmReadyToFly = False
finished      = False
msgCount      = 0 
timecode      = '00:00:00:00'
framerate     = 25

################################################  this module osc receiving:
RECEIVING_IP            = "0.0.0.0"
RECEIVING_PORT          = 9200
OSC_PROCESS_RATE        = 0.003
################################################  notch osc aggregator:
AGGREGATION_ENABLED       = True
AGGREGATOR_RECEIVING_PORT = 9201
aggregatorInstance      = None
aggregatorProcess       = None
aggregatorCue           = Queue()
aggregatorExitEvent     = None
posLock = Lock()

##################################################  global rates:
commandsFrequency               = 0.04   # actual command'd rate to uavss
RECEIVED_MESSAGES_SAMPLING_RATE = 10
###########################  companion
def setSendEnabled (*args):
    global isSendEnabled
    isSendEnabled = not isSendEnabled
    weMaySend(isSendEnabled)
    print(Fore.RED +  'Master della ricezione OSC: %s' % isSendEnabled)
    
def getSendEnabled():
    return isSendEnabled
def comè(uno): # è booleano oppure no?
    uno = uno *1
    return uno

   
def checkSwarmFlyability():
    def loppo():
        global isSwarmReadyToFly
        while not finished:
            time.sleep(0.1)
            swarmFlyabilityArray = []
            for drogno in drogni:
                if drogni[drogno].isReadyToFly : swarmFlyabilityArray.append(True)
                elif not drogni[drogno].isReadyToFly and not drogni[drogno].isEngaged: swarmFlyabilityArray.append(True)
                # if drogni[drogno].isReadyToFly and drogni[drogno].isEngaged and drogni[drogno].batterySag < 0.85: swarmFlyabilityArray.append(True)
                # if drogni[drogno].isReadyToFly and drogni[drogno].isEngaged: swarmFlyabilityArray.append(True)
                else: swarmFlyabilityArray.append(False)
            if all (swarmFlyabilityArray):
                isSwarmReadyToFly = True
                setFlyability(True)
                
            else:
                isSwarmReadyToFly = False
                setFlyability(False)
    swarmFlyabilityLoop = threading.Thread(name='flyabilityLoop', target=loppo).start()

###########################  whole swarm
def takeOff   (coddii, decollante):
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
def goLeft    (coddii, quanto):
        print('chief says we\'re gonna go leftwards by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goLeft(quanto)
def goRight   (coddii, quanto):
        print('chief says we\'re gonna go rightwards by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goRight(quanto)
def goForward (coddii, quanto):
        print('chief says we\'re gonna go forward by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goForward(quanto)
def goBack    (coddii, quanto):
        print('chief says we\'re gonna go back by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goBack(quanto)
def goUp      (coddii, quanto):
        print('chief says we\'re gonna go up by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goUp(quanto)
def goDown    (coddii, quanto):
        print('chief says we\'re gonna go down by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goDown(quanto)
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
def engage    (coddii, chi):
    if chi == 'all':    
        for drogno in drogni:
            if not drogni[drogno].isEngaged:
                drogni[drogno].isEngaged = True
                print(' %s  engaging' % chi )
            else:
                drogni[drogno].isEngaged = False
                print(' %s  disengaging' % chi )
    else:
        if not drogni[chi].isEngaged: drogni[chi].isEngaged = True
        else: drogni[chi].isEngaged = False

###########################  single fella
def printAndSendCoordinates():
    global drogni
    global bufferone
    while not finished:
        time.sleep(commandsFrequency)
        if isSendEnabled:
            for drogno in drogni:
                iddio = drogni[drogno].ID
                drogni[drogno].setRingColor(bufferone[iddio].requested_R, bufferone[iddio].requested_G, bufferone[iddio].requested_B)

                if drogni[drogno].is_connected and drogni[drogno].isEngaged:
                    # print ('il drone %s dovrebbe colorarsi a %s %s %s' %( bufferone[iddio].ID, bufferone[iddio].requested_R,bufferone[iddio].requested_G,bufferone[iddio].requested_B))
                    # with posLock:
                    drogni[drogno].goTo(bufferone[iddio].requested_X, bufferone[iddio].requested_Y, bufferone[iddio].requested_Z)
                    # print ('il drone %s dovrebbe andare a %s %s %s' %( bufferone[iddio].name, bufferone[iddio].requested_X,bufferone[iddio].requested_Y,bufferone[iddio].requested_Z))
    print ('Non potrò mai più inviare ai drogni comandi di movimento, mai più')

def printHowManyMessages():
    # howManyMessagesLock = Lock()
    def printa():
        while not finished:
            global msgCount
            time.sleep(RECEIVED_MESSAGES_SAMPLING_RATE)
            # with howManyMessagesLock:
            if msgCount > 0.:
                print('\nNegli ultimi %s secondi ho ricevuto la media di %s messaggi OSC al secondo.' % (RECEIVED_MESSAGES_SAMPLING_RATE ,str(msgCount/RECEIVED_MESSAGES_SAMPLING_RATE)))
            msgCount = 0
        print('D\'ora in poi la smetto di ricevere messaggi')

    threading.Thread(target=printa).start()

def setRequestedPos(address, args):
    global msgCount
    global timecode
    iddio      = int(address[-5])
    # print(timecode)
    # with posLock: 
    timecode   = args[0]
    bufferone[iddio].requested_X = round(float(args[1]),3)
    bufferone[iddio].requested_Y = round(float(args[2]),3)
    bufferone[iddio].requested_Z = round(float(args[3]),3)
    # print('Ciao sono il drone %s e ho ricevuto un comando di posizione!' %(iddio))
    msgCount += 1

def setRequestedCol(address, args):
    global msgCount
    iddio     = int(address[-7])
    # with colLock:
    msgCount += 1
    bufferone[iddio].requested_R = args[1]
    bufferone[iddio].requested_G = args[2]
    bufferone[iddio].requested_B = args[3]

def setCommandsRate(address, args):
    global commandsFrequency
    # print(args)
    if args[0] == '+':
        commandsFrequency += 0.05
    elif args[0] == '-':
        if commandsFrequency > 0 and commandsFrequency <= 0.05:
            commandsFrequency -= 0.01
        if commandsFrequency > 0:
            commandsFrequency -= 0.05
    commandsFrequency = round(commandsFrequency, 2)
    for drogno in drogni:
        drogni[drogno].commandsFrequency = commandsFrequency
    set_command_frequency(commandsFrequency)
    
    
    print(Fore.RED + 'commandsFrequency has been set to ' + str(commandsFrequency))

def start_server():      ######################    #### OSC init    #########    acts as main()
    """ one day we'd call this function main, that day hasn't come yet"""
    global finished 
    global bufferone
    global timecode
    osc_startup()
    # logging.basicConfig(format='%(asctime)s - %(threadName)s ø %(name)s - '  '%(levelname)s - %(message)s')
    # logger = logging.getLogger("osc")
    # logger.setLevel(logging.DEBUG)
    # osc_startup(logger=logger)

    osc_udp_server(RECEIVING_IP,             RECEIVING_PORT,   "receivingServer")
    print(Fore.GREEN + 'OSC receiving server initalized on',   RECEIVING_IP, RECEIVING_PORT)
    
 
   
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
    osc_method("/goUp",             goUp,            argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goDown",           goDown,          argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/kill",             kill,            argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/standBy",          standBy,         argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/wakeUp",           wakeUp,          argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/resetEstimator",   resetEstimator,  argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/ringColor",        ringColor,       argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)
    osc_method("/engage",           engage,          argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/companion/isSendEnabled", setSendEnabled, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/setCompanionRate", setCompanionRate, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/setCommandsRate",  setCommandsRate, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    
    ############################################################ loops on their own threads:
    printHowManyMessages()
    checkSwarmFlyability()
    ############################################################

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
