# -*- coding: utf-8 -*-
#rf 2022

# native modules
import logging, sys, os, multiprocessing, threading, time, signal
from   pathlib                    import Path
from   rich import print
 
#bitcraze modules  
CFLIB_PATH      = os.environ.get('CFLIB_PATH')  ############    CFLIB_PATH è assoluto e va specificato nel file .env su ogni macchina
sys.path = [CFLIB_PATH, *sys.path]                  ### Mette CFLIB_PATH all'inizio delle variabili d'ambiente
import cflib.crtp
from   cflib.utils.power_switch import PowerSwitch
from   cflib.utils import uri_helper
logging.basicConfig(level=logging.ERROR)

#custom modules
import OSCStuff   as OSC
import GUI        as GUI
import Drogno
import connections
import GLOBALS    as GB

def main():
    signal.signal(signal.SIGINT, exit_signal_handler)

    if GB.WE_ARE_FAKING_IT:
        print('ATTENZIONE! STIAMO FACENDO FINTA!')
        time.sleep(2)
        return
    
    
    print("Controller started. No fake shit.")
    set_trajectory_path()
    # GB.init()                          ## initialize exit events
    connections.radioStart()
    # connections.add_crazyflies()       ## chek if we already got CFs reachable
    connections.restart_devices()
    connections.create_classes()


    #send drogni's array to submodules
    OSC.faiIlBufferon()
    OSCRefreshThread      = threading.Thread(target=OSC.start_server).start()
    OSCPrintAndSendThread = threading.Thread(target=OSC.printAndSendCoordinates).start()

    GUI.startCompanionFeedback()
    time.sleep(0.6)
    GUI.reset_companion()
    GUI.start_companion_update()

    if GB.AUTO_RECONNECT:
        reconnectThread = threading.Thread(target=connections.autoReconnect).start()  

def exit_signal_handler(signum, frame):
    ciao_ciao()

def ciao_ciao():
    print('Bye bye.')
    GUI.reset_companion()
    OSC.finished = True
    GUI.ends_it_when_it_needs_to_end()
    GB.eventi.set_thread_exit_event() 
    GB.eventi.set_process_exit_event()

    for drogno in GB.drogni:
        if (drogno):
            try: PowerSwitch(GB.drogni[drogno].link_uri).stm_power_down()
            except Exception: print('While closing the program I wanted to shut down %s, which is unfortunately not there to be shut down' % GB.drogni[drogno].link_uri)
            GB.drogni[drogno].exit()
            GB.drogni[drogno].join()
    print('I said bye.')
   
    sys.exit("Putin merda")

def set_trajectory_path():
     # os.chdir(os.path.join('..', 'trajectoryRecorder', 'registrazioniOSC'))
    # patto = Path('./lastRecord.txt')
    # with open(patto, 'r') as f:
    #     lastRecordPath = f.read()
    #     print ('last record path: ' + lastRecordPath)
    pass

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
    main()
    while True:
        time.sleep(0.1)
        pass
        
