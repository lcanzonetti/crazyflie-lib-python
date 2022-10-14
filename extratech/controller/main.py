# -*- coding: utf-8 -*-
#rf 2022
# native modules
import logging, sys, os, multiprocessing, threading, time, signal
from   pathlib                    import Path
from rich import print
from dotenv import load_dotenv
load_dotenv()
#bitcraze modules  
CFLIB_PATH      = os.environ.get('CFLIB_PATH')  ############    CFLIB_PATH è assoluto e va specificato nel file .env su ogni macchina
# print(CFLIB_PATH)
sys.path = [CFLIB_PATH, *sys.path]                  ### Mette CFLIB_PATH all'inizio delle variabili d'ambiente
# print(*sys.path, sep='\n')
import cflib.crtp
from   cflib.utils.power_switch import PowerSwitch
from   cflib.utils import uri_helper

logging.basicConfig(level=logging.ERROR)

#custom modules
import OSCStuff       as OSC
import GUI as GUI
import Drogno
import connections
import GLOBALS as GB

threads_exit_event               = threading.Event()
processes_exit_event             = multiprocessing.Event()
connections.threads_exit_event   = threads_exit_event
connections.processes_exit_event = processes_exit_event

WE_ARE_FAKING_IT           = GB.WE_ARE_FAKING_IT
GUI.COMPANION_FEEDBACK_IP  = os.getenv("COMPANION_FEEDBACK_IP")
OSC.aggregatorExitEvent    = processes_exit_event 


connectedUris = GB.uris.copy()
drogni = {}

def radioStart():
    if not WE_ARE_FAKING_IT:
        cflib.crtp.init_drivers()
        print('Scanning usb for Crazy radios...')
        if (cflib.crtp.get_interfaces_status()['radio'] == 'Crazyradio not found'):
            raise Exception("no radio!")
        else:
            radios = cflib.crtp.get_interfaces_status()
            print("[bold blue]%s radio trovata:"%len(radios))
            print(radios)
    else: 
        print('simulo di aver trovato una radio')
        time.sleep(1)

def add_crazyflies():
    if WE_ARE_FAKING_IT:
        print('simulo di aver aggiunto i crazifliii')
        time.sleep(1) 
        return

    available_crazyfliess = []
    print('Scanning interfaces for Crazyflies...')
    for iuro in GB.uris:
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
        time.sleep(GB.RECONNECT_FREQUENCY)
        for drogno in drogni:
            if not drogni[drogno].isKilled:
                print('il drogno %s è sparito, provo a riconnettermi' % drogni[drogno].ID)
                IDToBeRenewed  = drogni[drogno].ID
                uriToBeRenewed = drogni[drogno].link_uri
                del drogni[drogno]
                drogni[IDToBeRenewed] = Drogno.Drogno(IDToBeRenewed, uriToBeRenewed, threads_exit_event, WE_ARE_FAKING_IT, GB.PREFERRED_STARTING_POINTS[IDToBeRenewed], GB.lastRecordPath)
                drogni[IDToBeRenewed].start()

def restart_devices():
    global connectedUris
    print('Restarting devices')

    if not WE_ARE_FAKING_IT:
        for uri in GB.uris:
            # time.sleep(0.5)
            try: PowerSwitch(uri).stm_power_down()
            except Exception:
                print('%s is not there to be shut down' % uri)
                # raise Exception
        print('GLOBALS.uris meant to be switched on:')
        print(GB.uris)
        urisToBeRemoved = []
        for urico in range(len(GB.uris)):
            try:
                # print('trying to power up %s' % GB.uris[urico]) 
                PowerSwitch(GB.uris[urico]).stm_power_up()
            except Exception: 
                print('%s is not there to be woken up, gonna pop it out from my list' % GB.uris[urico])
                urisToBeRemoved.append(GB.uris[urico])
        connectedUris = GB.uris.copy()
        for u in urisToBeRemoved:
            connectedUris.remove(u)
    else:
        connectedUris = GB.uris.copy()

    print('at the end these are drognos we have:')
    print(connectedUris)
    # if len(connectedUris) == 0:
    #     opinion = input('there actually no drognos, wanna retry?\nPress R to retry,\nQ to exit, or S to stand-by.')
    #     if opinion == 'r' or opinion == 'R':
    #         restart_devices()
    #     if opinion == 's' or opinion == 'S':
    #         return
    #     if opinion == 'q' or opinion == 'Q':
    #         sys.exit()
    # else:
    #     # Wait for devices to boot
    #     time.sleep(4)
    time.sleep(4)

def main():
    if WE_ARE_FAKING_IT:
        print('ATTENZIONE! STIAMO FACENDO FINTA!')
        time.sleep(2)
        return
    else:
        print("Controller started. No fake shit.")
    try:
        radioStart()
        # cflib.crtp.init_drivers()
        # add_crazyflies()
        restart_devices()

    except Exception as e:
        print(e)
        print('Nice try mate, ciao.')
        quit()

    for uro in connectedUris:
        iddio = IDFromURI(uro)
        drogni[iddio] = Drogno.Drogno(iddio, uro, threads_exit_event, processes_exit_event, WE_ARE_FAKING_IT, GB.PREFERRED_STARTING_POINTS[iddio], GB.lastRecordPath)
        drogni[iddio].start()
        print('i drogni:')
        print(drogni)

    #send drogni's array to submodules
    OSC.faiIlBufferon()
    GUI.drogni = drogni
    OSCRefreshThread      = threading.Thread(target=OSC.start_server).start()
    OSCPrintAndSendThread = threading.Thread(target=OSC.printAndSendCoordinates).start()


    GUI.startCompanionFeedback()
    time.sleep(0.6)
    GUI.resetCompanion()
    GUI.updateCompanion()

    if GB.AUTO_RECONNECT:
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

def IDFromURI(uri):
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
        
