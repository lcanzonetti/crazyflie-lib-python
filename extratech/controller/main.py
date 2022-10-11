# -*- coding: utf-8 -*-

#rf 2022
# native modules
import logging, sys, os, multiprocessing, threading, time, signal
from   pathlib                    import Path
#bitcraze modules
import cflib.crtp
from   cflib.utils.power_switch import PowerSwitch
from   cflib.utils import uri_helper
#custom modules
import OSCStuff       as OSC
import GUI as GUI
import Drogno
logging.basicConfig(level=logging.ERROR)
#########################################################################
uris = [    
        # 'radio://0/80/2M/E7E7E7E7E0',
        'radio://0/80/2M/E7E7E7E7E1',
        # 'radio://0/80/2M/E7E7E7E7E2',
        # 'radio://0/90/2M/E7E7E7E7E3',
        # 'radio://1/120/2M/E7E7E7E7E4', 
        # 'radio://0/80/2M/E7E7E7E7E5',
        # 'radio://3/100/2M/E7E7E7E7E6',
        # 'radio://3/100/2M/E7E7E7E7E7',
        # 'radio://2/100/2M/E7E7E7E7E8', 
        # 'radio://2/110/2M/E7E7E7E7E9',
        # 'radio://0/110/2M/E7E7E7E7EA',
        # 'radio://0/120/2M/E7E7E7E7EB',
        # 'radio://0/120/2M/E7E7E7E7EC',
        # 'radio://0/120/2M/E7E7E7E7ED',
        # 'radio://0/120/2M/E7E7E7E7EE',
        # 'radio://0/120/2M/E7E7E7E7EF',
        ]
        
#########################################################################

from dotenv import load_dotenv
load_dotenv()
lastRecordPath        = ''  
WE_ARE_FAKING_IT      = False
LOGGING_ENABLED       = False
AUTO_RECONNECT        = False
RECONNECT_FREQUENCY   = 1
COMMANDS_FREQUENCY    = 0.1
FEEDBACK_SENDING_PORT = 6000
BROADCAST_IP          = "192.168.1.21"

threads_exit_event   = threading.Event()
processes_exit_event = multiprocessing.Event()

Drogno.COMMANDS_FREQUENCY  = COMMANDS_FREQUENCY
Drogno.FEEDBACK_SENDING_IP = BROADCAST_IP
OSC.commandsFrequency      = COMMANDS_FREQUENCY
OSC.RECEIVING_IP           = os.getenv("RECEIVING_IP")
GUI.COMPANION_FEEDBACK_IP  = os.getenv("COMPANION_FEEDBACK_IP")
OSC.aggregatorExitEvent    = processes_exit_event 


connectedUris = uris.copy()
drogni = {}

SPACING = 0.5
PREFERRED_STARTING_POINTS =   [ ( -SPACING, SPACING),    (0, SPACING)   , (SPACING, SPACING), 
                                ( -SPACING, -0),         (0, 0)         , (SPACING, 0), 
                                ( -SPACING, -SPACING),   (0, -SPACING)  , (SPACING, -SPACING), 
                                ( -SPACING*1.5, -SPACING), (0, 0), (0,0) , (0,0), (0,0), (0,0), (0,0)
                                ]

def radioStart():
    if not WE_ARE_FAKING_IT:
        cflib.crtp.init_drivers()
        print('Scanning usb for Crazy radios...')

        if (cflib.crtp.get_interfaces_status()['radio'] == 'Crazyradio not found'):
            raise Exception("no radio!")
        else:
            print ('Radio trovata:')
            print(cflib.crtp.get_interfaces_status())


        available_crazyfliess = []
        
        print('Scanning interfaces for Crazyflies...')
        for iuro in uris:
            print ('looking for %s ' % iuro)
            available_crazyflies  = cflib.crtp.scan_interfaces(uri_helper.address_from_env(iuro))
            if available_crazyflies:
                available_crazyfliess.append(available_crazyflies)

        if available_crazyfliess:
            print(f'gente in giro:')
            print (available_crazyfliess)     

            # for i in available_crazyfliess:
            #     print ('Found %s radios.' % len(available_crazyfliess))
            #     print ("URI: [%s]   ---   name/comment [%s]" % (i[0], i[1]))
        else:
            print('no crazyflies?')     

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
                # raise Exception
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
    else:
        print("Controller started. No fake shit.")
    try:
        radioStart()
        restart_devices()

    except Exception as e:
        print(e)
        print('Nice try, mate, ciao ciao.')
        quit()

    for uro in connectedUris:
        iddio = IDFromURI(uro)
        drogni[iddio] = Drogno.Drogno(iddio, uro, threads_exit_event, processes_exit_event, WE_ARE_FAKING_IT, PREFERRED_STARTING_POINTS[iddio], lastRecordPath)
        drogni[iddio].start()
        print(drogni)

    #send drogni's array to submodules
    OSC.drogni = drogni
    OSC.faiIlBufferon()
    GUI.drogni = drogni
    # OSCRefreshThread      = threading.Thread(target=OSC.start_server,daemon=True).start()
    OSCRefreshThread      = threading.Thread(target=OSC.start_server).start()
    OSCPrintAndSendThread = threading.Thread(target=OSC.printAndSendCoordinates).start()


    GUI.startCompanionFeedback()
    time.sleep(0.6)
    GUI.resetCompanion()
    GUI.updateCompanion()

    if AUTO_RECONNECT:
        reconnectThread = threading.Thread(target=autoReconnect).start()  

def exit_signal_handler(signum, frame):
    ciao_ciao()

def ciao_ciao():
    print('Bye bye.')
    GUI.resetCompanion()
    OSC.finished = True
    GUI.ends_it_when_it_needs_to_end()
    threads_exit_event.set() 
    processes_exit_event.set()

    for drogno in drogni:
        if (drogno):
            try: PowerSwitch(drogni[drogno].link_uri).stm_power_down()
            except Exception: print('While closing the program I wanted to shut down %s, which is unfortunately not there to be shut down' % drogni[drogno].link_uri)
            drogni[drogno].exit()
            drogni[drogno].join()
    print('I said bye.')
   
    sys.exit("Putin merda")

def IDFromURI(uri) -> int:
    # Get the address part of the uri
    address = uri.rsplit('/', 1)[-1]
    try:
        # print(int(address, 16) - 996028180448)
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
    signal.signal(signal.SIGINT, exit_signal_handler)
    main()

    while True:
        time.sleep(0.1)
        pass
        
