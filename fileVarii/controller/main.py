#rf 2021
#ciao
import os
from pathlib import Path
import multiprocessing
import threading
import time
import signal
from   collections import namedtuple
#custom modules
import OSCStuff as OSC
import OSC_feedabcker as feedbacker
import Drogno
import cflib.crtp
import sys
# import power_switch_mod as PowerSwitch
from   cflib.utils.power_switch import PowerSwitch
from   multiprocessing.connection import Client

lastRecordPath   = ''  
WE_ARE_FAKING_IT    = False
AUTO_RECONNECT      = True
RECONNECT_FREQUENCY = 1
COMMANDS_FREQUENCY  = 0.2
FEEDBACK_SENDING_PORT = 6000

Drogno.COMMANDS_FREQUENCY = COMMANDS_FREQUENCY
OSC.COMMANDS_FREQUENCY    = COMMANDS_FREQUENCY

threads_exit_event   = threading.Event()
processes_exit_event = multiprocessing.Event()
OSCFeedbackProcess   = multiprocessing.Process(target=feedbacker.Feedbacco, args=[processes_exit_event])
address = ('127.0.0.1', FEEDBACK_SENDING_PORT)
connectionToFeedbackProcess = None

uris = [    
        'radio://0/80/2M/E7E7E7E7E0',
        'radio://0/80/2M/E7E7E7E7E1',
        'radio://0/80/2M/E7E7E7E7E2',
        'radio://1/90/2M/E7E7E7E7E3',
        'radio://1/90/2M/E7E7E7E7E4',
        'radio://1/90/2M/E7E7E7E7E5',
        'radio://2/100/2M/E7E7E7E7E6',
        'radio://2/100/2M/E7E7E7E7E7',
        'radio://2/100/2M/E7E7E7E7E8'
        # 'radio://3/110/2M/E7E7E7E7E9',
        # 'radio://0/110/2M/E7E7E7E7EA',
        ]
connectedUris = uris.copy()
drogni = {}
SPACING = 0.5
PREFERRED_STARTING_POINTS =   [ ( -SPACING, SPACING),    (0, SPACING)   , (SPACING, SPACING), 
                                ( -SPACING, -0),         (0, 0)         , (SPACING, 0), 
                                ( -SPACING, -SPACING),   (0, -SPACING)  , (SPACING, -SPACING), 
                                  ( -SPACING*1.5, -SPACING)
                                ]

def radioStart():
    global WE_ARE_FAKING_IT
    if not WE_ARE_FAKING_IT:
        try:
            cflib.crtp.init_drivers()
            print(cflib.crtp.get_interfaces_status())   
            availableRadios = cflib.crtp.scan_interfaces()
            if availableRadios:
                print('available:')
                print (availableRadios)     

                for i in availableRadios:
                    print ('Found %s radios.' % len(availableRadios))
                    print ("URI: [%s]   ---   name/comment [%s]" % (i[0], i[1]))
            else:
                # WE_ARE_FAKING_IT = True
                print('porcoMondo')     

                pass
        except IndexError:
            print(IndexError)


def autoReconnect():
    while not threads_exit_event.is_set() :
        time.sleep(RECONNECT_FREQUENCY)
        for drogno in drogni:
            if drogni[drogno].isKilled:
                print('il drogno %s è stato ucciso, provo a riconnettermi' % drogni[drogno].ID)
                IDToBeRenewed = drogni[drogno].ID
                uriToBeRenewed = drogni[drogno].link_uri
                del drogni[drogno]
                drogni[IDToBeRenewed] = Drogno.Drogno(IDToBeRenewed, uriToBeRenewed, threads_exit_event, WE_ARE_FAKING_IT, PREFERRED_STARTING_POINTS[IDToBeRenewed], lastRecordPath)
                drogni[IDToBeRenewed].start()

def restart_devices():
    global connectedUris
    print('Restarting devices')
    for uri in uris:
        # time.sleep(0.5)
        try: PowerSwitch(uri).stm_power_down()
        except: print('%s is not there to be shut down' % uri)
    
    print('uris meant to be switched on:')
    print(uris)
    urisToBeRemoved = []
    for urico in range(len(uris)):
        # print('tipo:  ')
        # print(uris[urico])
        try:
            print('trying to power up %s' % uris[urico]) 
            PowerSwitch(uris[urico]).stm_power_up()
        except Exception: 
            print('%s is not there to be woken up, gonna pop it out from my list' % uris[urico])
            # connectedUris.remove(uris[urico])
            urisToBeRemoved.append(uris[urico])
            # time.sleep(0.5)
    connectedUris = uris.copy()
    for u in urisToBeRemoved:
        connectedUris.remove(u)
    

    print('at the end these are drognos we have:')
    print(connectedUris)
    if len(connectedUris) == 0:
        opinion = input('there actually no drognos, wanna retry or fake it?\nPress R to retry,\nF to fake it,\nQ to exit,\nor any other key, to choose not to choose.')
        if opinion == 'f' or opinion == 'F':
            global WE_ARE_FAKING_IT
            WE_ARE_FAKING_IT = True
        if opinion == 'r' or opinion == 'R':
            restart_devices()
        if opinion == 'q' or opinion == 'Q':
            sys.exit()
    else:
        # Wait for devices to boot
        time.sleep(4)

def main():
    radioStart()
    restart_devices()

    for uro in connectedUris:
        iddio = int(uro[-1])
        drogni[iddio] = Drogno.Drogno(iddio, uro, threads_exit_event, WE_ARE_FAKING_IT, PREFERRED_STARTING_POINTS[iddio], lastRecordPath)
        drogni[iddio].start() 

    OSCFeedbackProcess.start()

    OSC.drogni = drogni
    OSC.faiIlBufferon()
    OSCRefreshThread      = threading.Thread(target=OSC.start_server,daemon=True).start()
    OSCPrintAndSendThread = threading.Thread(target=OSC.printAndSendCoordinates,daemon=True).start()
    if AUTO_RECONNECT:
        reconnectThread = threading.Thread(target=autoReconnect).start()  
    # time.sleep(2)
    global connectionToFeedbackProcess
    time.sleep(3)
    try:
        connectionToFeedbackProcess = Client(address)
    except:
        print('non trovo quaa mmerda de fidbeck')
    

def exit_signal_handler(signum, frame):
    global OSCFeedbackProcess 
    global threads_exit_event
    print('esco')
    processes_exit_event.set()
    threads_exit_event.set() 

    for drogno in drogni:
        drogni[drogno].exit()
        drogni[drogno].join()
    OSC.resetCompanion()
    OSC.finished = True

    connectionToFeedbackProcess.send('fuck you')
    OSCFeedbackProcess.join()
    # time.sleep(2)

    sys.exit()

if __name__ == '__main__':
    # os.chdir(os.path.join('..', 'trajectoryRecorder', 'registrazioniOSC'))
    # patto = Path('./lastRecord.txt')
    # with open(patto, 'r') as f:
    #     lastRecordPath = f.read()
    #     print ('last record path: ' + lastRecordPath)
    main()
    signal.signal(signal.SIGINT, exit_signal_handler)

    while True:
        pass

