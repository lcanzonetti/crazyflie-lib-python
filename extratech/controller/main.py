#rf 2022
# native modules
import logging
import sys
import multiprocessing
import threading
import time
import signal
from   pathlib                    import Path
#bitcraze modules
import cflib.crtp
from   cflib.utils.power_switch import PowerSwitch
from   cflib.utils import uri_helper
#custom modules
import OSCStuff       as OSC
import GUI as GUI
import Drogno
import logging
logging.basicConfig(level=logging.ERROR)
#########################################################################
uris = [    
        'radio://0/80/2M/E7E7E7E7E0',
        'radio://0/80/2M/E7E7E7E7E1',
        'radio://0/80/2M/E7E7E7E7E2',
        'radio://0/90/2M/E7E7E7E7E3',
        'radio://1/120/2M/E7E7E7E7E4', 
        'radio://0/80/2M/E7E7E7E7E5',
        'radio://3/100/2M/E7E7E7E7E6',
        'radio://3/100/2M/E7E7E7E7E7',
        'radio://2/100/2M/E7E7E7E7E8', 
        # 'radio://2/110/2M/E7E7E7E7E9',
        # 'radio://0/110/2M/E7E7E7E7EA',
        ]
        
#########################################################################

lastRecordPath        = ''  
WE_ARE_FAKING_IT      = True
AUTO_RECONNECT        = False
RECONNECT_FREQUENCY   = 1
COMMANDS_FREQUENCY    = 0.04
FEEDBACK_SENDING_PORT = 6000
BROADCAST_IP          = "192.168.10.255"

threads_exit_event   = threading.Event()
processes_exit_event = multiprocessing.Event()

Drogno.COMMANDS_FREQUENCY  = COMMANDS_FREQUENCY
Drogno.FEEDBACK_SENDING_IP = BROADCAST_IP
OSC.commandsFrequency      = COMMANDS_FREQUENCY
GUI.COMPANION_FEEDBACK_IP  = "192.168.1.255" 
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
    if not WE_ARE_FAKING_IT:
        try:
            cflib.crtp.init_drivers()
            print('Scanning interfaces for Crazyflies...')
            print(cflib.crtp.get_interfaces_status())
            availableRadios = []
            for iuro in uris:
                availableRadio  = cflib.crtp.scan_interfaces(uri_helper.address_from_env(iuro))
                if availableRadio:
                    availableRadios.append(availableRadio)

            if availableRadios:
                print(f'gente in giro:')
                print (availableRadios)     

                # for i in availableRadios:
                #     print ('Found %s radios.' % len(availableRadios))
                #     print ("URI: [%s]   ---   name/comment [%s]" % (i[0], i[1]))
            else:
                print('no available radios?')     
        except IndexError:
            print(IndexError)

def autoReconnect():
    while not threads_exit_event.is_set() :
        time.sleep(RECONNECT_FREQUENCY)
        for drogno in drogni:
            if not drogni[drogno].isKilled:
                print('il drogno %s è sparito, provo a riconnettermi' % drogni[drogno].ID)
                IDToBeRenewed  = drogni[drogno].ID
                uriToBeRenewed = drogni[drogno].link_uri
                del drogni[drogno]
                drogni[IDToBeRenewed] = Drogno.Drogno(IDToBeRenewed, uriToBeRenewed, threads_exit_event, WE_ARE_FAKING_IT, PREFERRED_STARTING_POINTS[IDToBeRenewed], lastRecordPath)
                drogni[IDToBeRenewed].start()

def restart_devices():
    global connectedUris
    print('Restarting devices')

    if not WE_ARE_FAKING_IT:
        for uri in uris:
            # time.sleep(0.5)
            try: PowerSwitch(uri).stm_power_down()
            except Exception:
                print('%s is not there to be shut down' % uri)
                raise Exception
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
    else:
        connectedUris = uris.copy()

    print('at the end these are drognos we have:')
    print(connectedUris)
    if len(connectedUris) == 0:
        opinion = input('there actually no drognos, wanna retry?\nPress R to retry,\nQ to exit.')
        if opinion == 'r' or opinion == 'R':
            restart_devices()
        if opinion == 'q' or opinion == 'Q':
            sys.exit()
    else:
        # Wait for devices to boot
        time.sleep(5)

def main():
    if WE_ARE_FAKING_IT:
        print('ATTENZIONE! STIAMO FACENDO FINTA!')
        time.sleep(2)
    radioStart()
    restart_devices()
 
    for uro in connectedUris:
        iddio = IDFromURI(uro)
        drogni[iddio] = Drogno.Drogno(iddio, uro, threads_exit_event, processes_exit_event, WE_ARE_FAKING_IT, PREFERRED_STARTING_POINTS[iddio], lastRecordPath)
        drogni[iddio].start() 

    #send drogni's array to submodules
    OSC.drogni = drogni
    OSC.faiIlBufferon()
    GUI.drogni = drogni
    # OSCRefreshThread      = threading.Thread(target=OSC.start_server,daemon=True).start()
    OSCRefreshThread      = threading.Thread(target=OSC.start_server).start()
    OSCPrintAndSendThread = threading.Thread(target=OSC.printAndSendCoordinates).start()


    GUI.startCompanionFeedback()
    time.sleep(1)
    GUI.resetCompanion()
    GUI.updateCompanion()

    if AUTO_RECONNECT:
        reconnectThread = threading.Thread(target=autoReconnect).start()  

def exit_signal_handler(signum, frame):
    print('esco')
    GUI.resetCompanion()
    OSC.finished = True
    GUI.ends_it_when_it_needs_to_end()
    threads_exit_event.set() 
    processes_exit_event.set()

    for drogno in drogni:
        try: PowerSwitch(drogni[drogno].link_uri).stm_power_down()
        except Exception: print('While closing the program I wanted to shut down %s, which is unfortunately not there to be shut down' % drogni[drogno].link_uri)
        drogni[drogno].exit()
        drogni[drogno].join()
   
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
        time.sleep(0.1)
        pass
        
