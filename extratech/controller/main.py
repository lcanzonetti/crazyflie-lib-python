#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#rf 2022

# native modules
import logging, sys, os, threading, time, signal
from   rich import print
from PIL import Image, ImageDraw, ImageFont
import numpy as np

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

finished = False

def main():
    print_greetings()

    if GB.WE_ARE_FAKING_IT:
        print('ATTENZIONE! STIAMO FACENDO FINTA!')
    
    else:
        print("Controller started. No fake shit.")
        try:
            connections.radioStart()
        except Exception as e:
            print(e)
            ciao_ciao('ciao', 'ciao')
        connections.add_crazyflies()       ## chek if we already got CFs reachable
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

def ciao_ciao(signum, frame):
    print('Bye bye. \n%s' % signum)
    GUI.reset_companion()
    OSC.finished = True
    GUI.ends_it_when_it_needs_to_end()
    GB.eventi.set_thread_exit_event() 
    GB.eventi.set_process_exit_event()

    try:
        for drogno in GB.drogni:
            if (drogno):
                try: PowerSwitch(GB.drogni[drogno].link_uri).stm_power_down()
                except Exception: print('While closing the program I wanted to shut down %s, which is unfortunately not there to be shut down' % GB.drogni[drogno].link_uri)
                GB.drogni[drogno].exit()
                GB.drogni[drogno].join()
    except Exception as e:
        print(e)
    print('I said bye.')
    global finished
    finished = True
    sys.exit("Putin merda")
     

def print_greetings():
    text   = "extratech swarm controller"
    myfont = ImageFont.load_default()
    size   = myfont.getsize(text)
    img    = Image.new("1",size,"black")
    draw   = ImageDraw.Draw(img)
    draw.text((0, 0), text, "white", font=myfont)
    pixels = np.array(img, dtype=np.uint8)
    chars = np.array([' ','#'], dtype="U1")[pixels]
    strings = chars.view('U' + str(chars.shape[1])).flatten()
    os.system("cls")
    print( "\n".join(strings))
    print('\n')

if __name__ == '__main__':
    signal.signal(signal.SIGINT, ciao_ciao) ## cattura il control+C e gli fa fare il ciao, ciao 

    main()
    while not finished:
        time.sleep(0.1)
        pass
        
