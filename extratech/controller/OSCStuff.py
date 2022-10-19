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
import time, os
import numpy as np
from   osc4py3.as_eventloop  import *
from   osc4py3               import oscmethod as osm
from   osc4py3               import oscbuildparse


from   colorama              import Fore, Back, Style
from   colorama              import init as coloInit  
coloInit(convert=True)
import GLOBALS as GB
import connections
import OSC_aggregator
from GUI import setCompanionRate, setFlyability, set_command_frequency,weMaySend

bufferone         = {}
isSendEnabled     = False
isSwarmReadyToFly = False
finished          = False
msgCount          = 0 
timecode          = '00:00:00:00'
framerate         = 25
add_one = None

aggregatorInstance        = None
aggregatorProcess         = None
aggregatorCue             = Queue()
aggregatorExitEvent       = multiprocessing.Event()
posLock = Lock()


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
            for drogno in GB.drogni:
                if GB.drogni[drogno].isReadyToFly : swarmFlyabilityArray.append(True)
                elif not GB.drogni[drogno].isReadyToFly and not GB.drogni[drogno].isEngaged: swarmFlyabilityArray.append(True)
                # if GB.drogni[drogno].isReadyToFly and GB.drogni[drogno].isEngaged and GB.drogni[drogno].batterySag < 0.85: swarmFlyabilityArray.append(True)
                # if GB.drogni[drogno].isReadyToFly and GB.drogni[drogno].isEngaged: swarmFlyabilityArray.append(True)
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
    def authorizedScrambleCommand():
        for drogno in GB.drogni:
            bufferone[GB.drogni[drogno].ID].requested_X = GB.drogni[drogno].x
            bufferone[GB.drogni[drogno].ID].requested_Y = GB.drogni[drogno].y
            GB.drogni[drogno].takeOff()

    authorizedDrognos = 0
    if decollante == 'all':    # whole swarm logic
        print('chief says %s gonna take the fuck off' %(decollante))
        for drogno in GB.drogni:
            if GB.drogni[drogno].is_connected and GB.drogni[drogno].evaluateFlyness():               
                authorizedDrognos += 1
                print(Fore.WHITE + 'Got %s drognos ready to scramble.' % authorizedDrognos)
                if authorizedDrognos == len(GB.drogni):
                    print(Fore.GREEN + 'Got ENOUGH drognos ready to scramble!')
                    authorizedScrambleCommand()
            else:
                print('can\'t scramble drogno %s, not connected or not ready' % GB.drogni[drogno].name)
    else:                         # single drogno logic, scramble or land
        if GB.drogni[decollante].is_connected:
            if not GB.drogni[decollante].isFlying:   # if it is not flying
                print('chief says %s gonna take the fuck off' %(GB.drogni[decollante]))
                if GB.drogni[decollante].evaluateFlyness():  # and might fly
                    bufferone[GB.drogni[decollante].ID].requested_X = GB.drogni[decollante].x
                    bufferone[GB.drogni[decollante].ID].requested_Y = GB.drogni[decollante].y
                    try:
                        gino = threading.Thread(target=GB.drogni[decollante].takeOff).start()
                        # GB.drogni[decollante].takeOff(0.45, 2.45)
                    except Exception:
                        print('already taking off %s' % Exception)
                else: 
                    print('drone %s is not ready to fly' % GB.drogni[decollante])
            else:            #if is flying already it may very well land
                print('chief says %s gonna land' %(decollante))
                GB.drogni[decollante].land()
        else:
            print('il drogno %s non è connesso' % GB.drogni[decollante].name)
def uploadSequence(coddii,quale):
        print('chief says we\'re upload shit at sequence %s' % quale)
        for drogno in GB.drogni:
            if GB.drogni[drogno].is_connected:
                GB.drogni[drogno].upload_trajectory(quale)
            else:
                print('il drogno %s non è connesso' % GB.drogni[drogno].name)
def startTestSequence (coddii,quale):
        print('chief says we\'re gonna do testsss at sequence %s' % quale)
        for drogno in GB.drogni:
            if GB.drogni[drogno].is_connected:
                print('TEST!')
                GB.drogni[drogno].testSequence(quale)
            else:
                print('il drogno %s non è connesso' % GB.drogni[drogno].name)
def go        (coddii,quale):
        print('chief says we\'re gonna do shit at sequence %s' % quale)
        for drogno in GB.drogni:
            if GB.drogni[drogno].is_connected:
                GB.drogni[drogno].go(quale)
def goLeft    (coddii, quanto):
        print('chief says we\'re gonna go leftwards by %s ' % quanto)
        for drogno in GB.drogni:
            if GB.drogni[drogno].is_connected:
                GB.drogni[drogno].goLeft(quanto)
def goRight   (coddii, quanto):
        print('chief says we\'re gonna go rightwards by %s ' % quanto)
        for drogno in GB.drogni:
            if GB.drogni[drogno].is_connected:
                GB.drogni[drogno].goRight(quanto)
def goForward (coddii, quanto):
        print('chief says we\'re gonna go forward by %s ' % quanto)
        for drogno in GB.drogni:
            if GB.drogni[drogno].is_connected:
                GB.drogni[drogno].goForward(quanto)
def goBack    (coddii, quanto):
        print('chief says we\'re gonna go back by %s ' % quanto)
        for drogno in GB.drogni:
            if GB.drogni[drogno].is_connected:
                GB.drogni[drogno].goBack(quanto)
def goUp      (coddii, quanto):
        print('chief says we\'re gonna go up by %s ' % quanto)
        for drogno in GB.drogni:
            if GB.drogni[drogno].is_connected:
                GB.drogni[drogno].goUp(quanto)
def goDown    (coddii, quanto):
        print('chief says we\'re gonna go down by %s ' % quanto)
        for drogno in GB.drogni:
            if GB.drogni[drogno].is_connected:
                GB.drogni[drogno].goDown(quanto)
def land      (bullshit, landingCandidate):
    print('chief says %s gotta be grounded' % (landingCandidate))
    if landingCandidate == 'all':    
        for drogno in GB.drogni:
            if GB.drogni[drogno].is_connected:
                GB.drogni[drogno].land()
            else:
                print('il drogno %s non è connesso' % GB.drogni[drogno].name)
    else:
        GB.drogni[landingCandidate].land()
def home      (coddii, chi):
        print('chief says drogno_%s gonna go home' % chi)
        if GB.drogni[chi].is_connected:
            if GB.drogni[chi].isFlying:
                GB.drogni[chi].goHome()
            else:
                print('il drogno %s non è connesso' % GB.drogni[chi].name)
def goToStart (coddii, chi):
        print('chief says we (%s) are back at the start.' % chi)
        for drogno in GB.drogni:
            if GB.drogni[drogno].is_connected:
                GB.drogni[drogno].goToStart()
def ringColor (*args):
    # print('how fancy would it be to all look %s %s %s ?' % (args[1][0], args[1][1], args[1][2]) )
    # print (bullshit)
    # print  (rgb[0])
    for drogno in GB.drogni:
        if GB.drogni[drogno].is_Connected:
            GB.drogni[drogno].setRingColor(args[1][0], args[1][1], args[1][2])
        # GB.drogni[drogno].alternativeSetRingColor(args)
def kill      (coddii, chi):
    print(' %s  fuck now' % chi )
    if chi == 'all':    
        for drogno in GB.drogni:
            GB.drogni[drogno].killMeHardly()
    else:
        GB.drogni[chi].killMeHardly()
carlo = ''
def cambiaCarlo(funzione):
    global carlo
    carlo = funzione
def standBy   (coddii, chi):
    if chi == 'all':    
        print('addormenterei tutti' )
        for drogno in GB.drogni:
            GB.drogni[drogno].goToSleep()
    else:  ## singolo
        print('Attualmente nello sciame: %s' % GB.drogni)
        if not int(chi) in GB.drogni:
            print ( 'Il drogno che vuoi raggiungere non è ancora in lista')
            print ( 'kaaaaaaaaaaaaaaa---------------')
            connections.add_just_one_crazyflie(GB.uri_map[str(chi)])
            print( '-----------------booooooooooom')
        else:
            print ( 'Il drogno che vuoi è già in lista, in standby? %s' % GB.drogni[int(chi)].standBy)
            if GB.drogni[int(chi)].standBy == False:
                print('addormento %s' % chi)
                GB.drogni[int(chi)].goToSleep()
            else:
                print('sveglio %s' % chi)
                GB.drogni[int(chi)].wakeUp()
def wakeUp    (coddii, chi):
    print(' %s  wakes up' % chi )
    if chi == 'all':    
        for drogno in GB.drogni:
            GB.drogni[drogno].wakeUp()
    else:
        GB.drogni[chi].wakeUp()
def resetEstimator  (coddii, chi):
    # print(' %s  resetEstimator' % chi )
    if chi == 'all':    
        for drogno in GB.drogni:
            GB.drogni[drogno].resetEstimator()
    else:
        GB.drogni[chi].resetEstimator()
def engage    (coddii, chi):
    if chi == 'all':    
        for drogno in GB.drogni:
            if not GB.drogni[drogno].isEngaged:
                GB.drogni[drogno].isEngaged = True
                print(' %s  engaging' % chi )
            else:
                GB.drogni[drogno].isEngaged = False
                print(' %s  disengaging' % chi )
    else:
        if not GB.drogni[chi].isEngaged: GB.drogni[chi].isEngaged = True
        else: GB.drogni[chi].isEngaged = False
def enable_log(coddii, chi):
    if chi == 'all':    
        for drogno in GB.drogni:
            if not GB.drogni[drogno].isLogEnabled:
                GB.drogni[drogno].isLogEnabled = True
                print(' enabling Logging for %s' % chi )
            else:
                GB.drogni[drogno].isLogEnabled = False
                print(' disabling Logging for %s' % chi )

    else:
        if not GB.drogni[chi].isLogEnabled: GB.drogni[chi].isLogEnabled = True
        else: GB.drogni[chi].isLogEnabled = False
###########################  single fella
def printAndSendCoordinates():
    while not finished:
        time.sleep(GB.commandsFrequency)
        if isSendEnabled:
            for drogno in GB.drogni:
                iddio = GB.drogni[drogno].ID
                GB.drogni[drogno].setRingColor(bufferone[iddio].requested_R, bufferone[iddio].requested_G, bufferone[iddio].requested_B)

                if GB.drogni[drogno].is_connected and GB.drogni[drogno].isEngaged:
                    # print ('il drone %s dovrebbe colorarsi a %s %s %s' %( bufferone[iddio].ID, bufferone[iddio].requested_R,bufferone[iddio].requested_G,bufferone[iddio].requested_B))
                    # with posLock:
                    GB.drogni[drogno].goTo(bufferone[iddio].requested_X, bufferone[iddio].requested_Y, bufferone[iddio].requested_Z)
                    # print ('il drone %s dovrebbe andare a %s %s %s' %( bufferone[iddio].name, bufferone[iddio].requested_X,bufferone[iddio].requested_Y,bufferone[iddio].requested_Z))
    print ('Non potrò mai più inviare ai GB.drogni comandi di movimento, mai più')
def printHowManyMessages():
    # howManyMessagesLock = Lock()
    def printa():
        while not finished:
            global msgCount
            time.sleep(GB.RECEIVED_MESSAGES_SAMPLING_RATE)
            # with howManyMessagesLock:
            if msgCount > 0.:
                print('\nNegli ultimi %s secondi ho ricevuto la media di %s messaggi OSC al secondo.' % (GB.RECEIVED_MESSAGES_SAMPLING_RATE ,str(msgCount/GB.RECEIVED_MESSAGES_SAMPLING_RATE)))
            msgCount = 0
        print('D\'ora in poi la smetto di ricevere messaggi')

    threading.Thread(target=printa).start()
def setRequestedPos(address, args):
    global msgCount
    global timecode

    x = address.split('/')
    y = x[2].split('_')

    iddio = int(y[1])
    
    
    # print(timecode)
    # with posLock: 
    timecode   = args[0]
    bufferone[iddio].requested_X = round(float(args[1]),3)
    bufferone[iddio].requested_Y = round(float(args[2]),3)
    bufferone[iddio].requested_Z = round(float(args[3]),3)
    print('Ciao sono il drone %s e dovrei andare a X %s, Y %s, Z %s!!' %(iddio,round(float(args[1]),3), round(float(args[2]),3), round(float(args[3]),3)))
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
    # global GB.commandsFrequency
    # print(args)
    if args[0] == '+':
        GB.commandsFrequency += 0.05
    elif args[0] == '-':
        if GB.commandsFrequency > 0 and GB.commandsFrequency <= 0.05:
            GB.commandsFrequency -= 0.01
        if GB.commandsFrequency > 0:
            GB.commandsFrequency -= 0.05
    GB.commandsFrequency = round(GB.commandsFrequency, 2)
    for drogno in GB.drogni:
        GB.drogni[drogno].GB.commandsFrequency = GB.commandsFrequency
    set_command_frequency(GB.commandsFrequency)
    print(Fore.RED + 'commandsFrequency has been set to ' + str(GB.commandsFrequency))
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

    osc_udp_server(GB.RECEIVING_IP,             GB.RECEIVING_PORT,   "receivingServer")
    print(Fore.GREEN + 'OSC receiving server initalized on',   GB.RECEIVING_IP, GB.RECEIVING_PORT)
   
    if GB.AGGREGATION_ENABLED:
        pass
        # global aggregatorInstance
        # global aggregatorProcess
        # aggregatorInstance = OSC_aggregator.Aggregator(aggregatorExitEvent, aggregatorCue, AGGREGATOR_RECEIVING_PORT, bufferone, OSC_PROCESS_RATE, framerate )
        # aggregatorProcess  = Process(target=aggregatorInstance.start)
        # aggregatorProcess.daemon = True
        # aggregatorProcess.start() 
    
    ###########################  single fella requested position
    osc_method("/notch/drone*/pos",   setRequestedPos, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)
    osc_method("/notch/drone*/color", setRequestedCol, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)
    ###########################  swarm or single commnands
    osc_method("/takeOff",          takeOff,         argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/startTest",        startTestSequence, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
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
    osc_method("/enable_log",       enable_log,      argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
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
        time.sleep(GB.OSC_PROCESS_RATE)
        osc_process()
        if GB.AGGREGATION_ENABLED:
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
        time.sleep(1)
        pass
