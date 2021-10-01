#rf 2021
# native modules
import os
import sys
import multiprocessing
import threading
import time
import signal
from   pathlib                    import Path
#bitcraze modules
import cflib.crtp
from   cflib.utils.power_switch import PowerSwitch
#custom modules
import OSCStuff       as OSC
import Drogno
#########################################################################
uris = [    
        'radio://0/80/2M/E7E7E7E7E0',
        # 'radio://0/80/2M/E7E7E7E7E1',
        # 'radio://0/80/2M/E7E7E7E7E2',
        # 'radio://1/90/2M/E7E7E7E7E3',
        # 'radio://1/90/2M/E7E7E7E7E4',
        # 'radio://1/90/2M/E7E7E7E7E5',
        'radio://2/100/2M/E7E7E7E7E6',
        # 'radio://2/100/2M/E7E7E7E7E7',
        'radio://2/100/2M/E7E7E7E7E8'
        # 'radio://2/110/2M/E7E7E7E7E9',
        # 'radio://0/110/2M/E7E7E7E7EA',
        ]
        
#########################################################################

lastRecordPath        = ''  
WE_ARE_FAKING_IT      = False
AUTO_RECONNECT        = False
RECONNECT_FREQUENCY   = 1
COMMANDS_FREQUENCY    = 0.15
FEEDBACK_SENDING_PORT = 6000
BROADCAST_IP          = "192.168.10.255"

threads_exit_event   = threading.Event()
processes_exit_event = multiprocessing.Event()

Drogno.COMMANDS_FREQUENCY  = COMMANDS_FREQUENCY
Drogno.FEEDBACK_SENDING_IP = BROADCAST_IP
OSC.COMMANDS_FREQUENCY     = COMMANDS_FREQUENCY
OSC.COMPANION_FEEDBACK_IP  = BROADCAST_IP 
OSC.aggregatorExitEvent    = processes_exit_event 


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
                print('no radios?')     

                pass
        except IndexError:
            print(IndexError)

def autoReconnect():
    while not threads_exit_event.is_set() :
        time.sleep(RECONNECT_FREQUENCY)
        for drogno in drogni:
            if not drogni[drogno].isKilled:
                print('il drogno %s è sparito, provo a riconnettermi' % drogni[drogno].ID)
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
        try:
            # print('trying to power up %s' % uris[urico]) 
            PowerSwitch(uris[urico]).stm_power_up()
        except Exception: 
            print('%s is not there to be woken up, gonna pop it out from my list' % uris[urico])
            urisToBeRemoved.append(uris[urico])
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
        time.sleep(5)

def main():
    radioStart()
    restart_devices()
 
    for uro in connectedUris:
        iddio = IDFromURI(uro)
        drogni[iddio] = Drogno.Drogno(iddio, uro, threads_exit_event, processes_exit_event, WE_ARE_FAKING_IT, PREFERRED_STARTING_POINTS[iddio], lastRecordPath)
        drogni[iddio].start() 

    OSC.drogni = drogni
    OSC.faiIlBufferon()
    # OSCRefreshThread      = threading.Thread(target=OSC.start_server,daemon=True).start()
    OSCRefreshThread      = threading.Thread(target=OSC.start_server).start()
    OSCPrintAndSendThread = threading.Thread(target=OSC.printAndSendCoordinates).start()
    if AUTO_RECONNECT:
        reconnectThread = threading.Thread(target=autoReconnect).start()  

def exit_signal_handler(signum, frame):
    print('esco')
    OSC.resetCompanion()
    OSC.finished = True
    threads_exit_event.set() 
    processes_exit_event.set()

    for drogno in drogni:
        try: PowerSwitch(drogni[drogno].link_uri).stm_power_down()
        except: print('%s is not there to be shut down' % drogni[drogno].link_uri)
        drogni[drogno].exit()
        # drogni[drogno].join()
   
    sys.exit()

def IDFromURI(uri) -> int:
    # Get the address part of the uri
    address = uri.rsplit('/', 1)[-1]
    try:
        return int(address, 16) - 996028180448
    except ValueError:
        print('address is not hexadecimal! (%s)' % address, file=sys.stderr)
        return None

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
        
