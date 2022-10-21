# -*- coding: utf-8 -*-
#rf 2022

# native modules
import logging, sys, os, threading, time, signal
import ssl
from re import S
from   rich import print

#bitcraze modules  
CFLIB_PATH      = os.environ.get('CFLIB_PATH')  ############    CFLIB_PATH è assoluto e va specificato nel file .env su ogni macchina
sys.path        = [CFLIB_PATH, *sys.path]                  ### Mette CFLIB_PATH all'inizio delle variabili d'ambiente
from   cflib.utils.power_switch import PowerSwitch
from   cflib.utils import uri_helper
logging.basicConfig(level=logging.ERROR)

#custom modules
import OSCStuff   as OSC
import GUI       
import connections
import trajectories
import GLOBALS    as GB


def main():
    print_greetings()

    if GB.WE_ARE_FAKING_IT:
        print('ATTENZIONE! STIAMO FACENDO FINTA!')
    
    else:
        print("Controller started. No fake shit.")
        connections.radioStart()
        # connections.add_crazyflies()       ## chek if we already got CFs reachable
        connections.restart_devices()
        connections.create_classes()

    trajectories.set_trajectory_path()
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

def exit_signal_handler(signum, frame):
    ciao_ciao()

def print_greetings():
    text = "extratech swarm controller"
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    myfont = ImageFont.truetype("verdanab.ttf", 12)
    size = myfont.getsize(text)
    img = Image.new("1",size,"black")
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, "white", font=myfont)
    pixels = np.array(img, dtype=np.uint8)
    chars = np.array([' ','#'], dtype="U1")[pixels]
    strings = chars.view('U' + str(chars.shape[1])).flatten()
    print( "\n".join(strings))
    print('\n')
if __name__ == '__main__':
    signal.signal(signal.SIGINT, exit_signal_handler) 

    main()
    while True:
        time.sleep(0.1)
        pass
        
