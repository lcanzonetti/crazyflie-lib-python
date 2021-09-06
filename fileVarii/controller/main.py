#rf 2021
#ciao
import os
from pathlib import Path

import threading
import time
import signal
from   collections import namedtuple
#custom modules
import OSCStuff as OSC
import Drogno
import cflib.crtp
import sys

lastRecordPath   = ''  
WE_ARE_FAKING_IT    = True
AUTO_RECONNECT      = True
RECONNECT_FREQUENCY = 1
COMMANDS_FREQUENCY  = 0.2
Drogno.COMMANDS_FREQUENCY = COMMANDS_FREQUENCY
OSC.COMMANDS_FREQUENCY    = COMMANDS_FREQUENCY


exit_event = threading.Event()

uris = [
        # 'radio://0/80/2M/E7E7E7E7E0',
        # gut
        # 'radio://0/80/2M/E7E7E7E7E1',
        # gut
        # 'radio://0/80/2M/E7E7E7E7E2',
        # possibili problemi hardware
        # 'radio://1/90/2M/E7E7E7E7E3',
        #  (vuoti d'aria?)
        # 'radio://1/90/2M/E7E7E7E7E4',
        # grande incertezza al centro - super compensazioni
        # 'radio://1/90/2M/E7E7E7E7E5',
        #  gut  
        # 'radio://2/100/2M/E7E7E7E7E6',
        #  gut  -il meglio
        'radio://2/100/2M/E7E7E7E7E7',
        # serii problemi radio
        # 'radio://2/100/2M/E7E7E7E7E8',
        #  gut
        # 'radio://3/110/2M/E7E7E7E7E9',
        #  gut
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
    while not exit_event.is_set() :
        time.sleep(RECONNECT_FREQUENCY)
        for drogno in drogni:
            if drogni[drogno].isKilled:
                print('il drogno %s è stato ucciso, provo a riconnettermi' % drogni[drogno.ID])
                IDToBeRenewed = drogni[drogno].ID
                uriToBeRenewed = drogni[drogno].link_uri
                del drogni[drogno]
                drogni[IDToBeRenewed] = Drogno.Drogno(IDToBeRenewed, uriToBeRenewed, exit_event, WE_ARE_FAKING_IT, PREFERRED_STARTING_POINTS[IDToBeRenewed], lastRecordPath)
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
    
    for uro in uris:
        iddio = int(uro[-1])
        drogni[iddio] = Drogno.Drogno(iddio, uro, exit_event, WE_ARE_FAKING_IT, PREFERRED_STARTING_POINTS[iddio], lastRecordPath)
        drogni[iddio].start()

    OSC.drogni = drogni
    OSC.faiIlBufferon()
    OSCRefreshThread      = threading.Thread(target=OSC.start_server,daemon=True).start()
    OSCPrintAndSendThread = threading.Thread(target=OSC.printAndSendCoordinates,daemon=True).start()
    if AUTO_RECONNECT:
        reconnectThread = threading.Thread(target=autoReconnect).start()  

def exit_signal_handler(signum, frame):
    print('esco')
    exit_event.set() 
    OSC.finished = True
    drogni = {}
    sys.exit()

if __name__ == '__main__':
    os.chdir(os.path.join('..', 'trajectoryRecorder', 'registrazioniOSC'))
    patto = Path('./lastRecord.txt')
    with open(patto, 'r') as f:
        lastRecordPath = f.read()
        print ('last record path: ' + lastRecordPath)
    main()
    signal.signal(signal.SIGINT, exit_signal_handler)

    while True:
        pass

