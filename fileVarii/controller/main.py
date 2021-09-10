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


lastRecordPath   = ''  
WE_ARE_FAKING_IT    = False
AUTO_RECONNECT      = True
RECONNECT_FREQUENCY = 1
COMMANDS_FREQUENCY  = 0.2
Drogno.COMMANDS_FREQUENCY = COMMANDS_FREQUENCY
OSC.COMMANDS_FREQUENCY    = COMMANDS_FREQUENCY


threads_exit_event   = threading.Event()
processes_exit_event = multiprocessing.Event()
OSCFeedbackProcess   = multiprocessing.Process(target=feedbacker.feedbacco, args=[processes_exit_event])

uris = [    
        # 'radio://0/80/2M/E7E7E7E7E0',
        # 'radio://0/80/2M/E7E7E7E7E1',
        # 'radio://0/80/2M/E7E7E7E7E2',
        'radio://1/90/2M/E7E7E7E7E3',
        # 'radio://1/90/2M/E7E7E7E7E4',
        # 'radio://1/90/2M/E7E7E7E7E5',
        # 'radio://2/100/2M/E7E7E7E7E6',
        # 'radio://2/100/2M/E7E7E7E7E7',
        # 'radio://2/100/2M/E7E7E7E7E8',
        # 'radio://3/110/2M/E7E7E7E7E9',
        # 'radio://0/110/2M/E7E7E7E7EA',
        ]
drogni = {}
SPACING = 0.5
PREFERRED_STARTING_POINTS =   [ ( -SPACING, SPACING),    (0, SPACING)   , (SPACING, SPACING), 
                                ( -SPACING, -0),         (0, 0)         , (SPACING, 0), 
                                ( -SPACING, -SPACING),   (0, -SPACING)  , (SPACING, -SPACING), 
                                  ( -SPACING*1.5, -SPACING)
                                ]


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
 

def main():
    global WE_ARE_FAKING_IT
    if not WE_ARE_FAKING_IT:
        cflib.crtp.init_drivers(enable_debug_driver=False)
        print(cflib.crtp.get_interfaces_status())

    try:
        availableRadios = cflib.crtp.scan_interfaces()
        if availableRadios:
            for i in availableRadios:
                print ('Found %s radios.' % len(availableRadios))
                print ("URI: [%s]   ---   name/comment [%s]" % (i[0], i[1]))
        else:
            # WE_ARE_FAKING_IT = True
            pass
    except IndexError:
        print(IndexError)
    OSCFeedbackProcess.start()
    

    for uro in uris:
        iddio = int(uro[-1])
        drogni[iddio] = Drogno.Drogno(iddio, uro, threads_exit_event, WE_ARE_FAKING_IT, PREFERRED_STARTING_POINTS[iddio], lastRecordPath)
        drogni[iddio].start() 

    OSC.drogni = drogni
    OSC.faiIlBufferon()
    OSCRefreshThread      = threading.Thread(target=OSC.start_server,daemon=True).start()
    OSCPrintAndSendThread = threading.Thread(target=OSC.printAndSendCoordinates,daemon=True).start()

    
    if AUTO_RECONNECT:
        reconnectThread = threading.Thread(target=autoReconnect).start()  

def exit_signal_handler(signum, frame):
    global OSCFeedbackProcess 
    global threads_exit_event
    print('esco')
    threads_exit_event.set() 
    processes_exit_event.set()
    OSCFeedbackProcess.join()
    time.sleep(4)
    for drogno in drogni:
        drogni[drogno].exit()
        # drogni[drogno].join()
    OSC.resetCompanion()
    OSC.finished = True
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

