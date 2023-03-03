#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#rf 2023

import time, sys, threading, logging, signal, math, datetime, os, pathlib, shutil, msvcrt
from itertools import cycle

import argparse
import math

from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server

import pandas as pd
from time import perf_counter
from timeloop import Timeloop
from datetime import timedelta
tl = Timeloop()
cartella_registrazioni           = 'registrazioniOSC'
if not pathlib.Path(cartella_registrazioni).exists():
  os.mkdir(cartella_registrazioni) 

tab = '\t'

lead_IN           = 200
lead_OUT          = 118500
numero_drogni     = 9
intervallo        = 0.1
porta             = 9202
loop              = cycle(r"-\|/")
bufferone         = {}
timecode          = 0
tempo_di_inizio        = 0
finished          = False
recording         = False 
righe             = 0
is_automatic      = True

def runnnn():
    print("running ...", next(loop), end='\r', flush=True)

def setRequestedPos_X(add, roba):
    drone_stringa      = add.split('/')[2]
    iddio              = int(drone_stringa[5:])
    bufferone[iddio].x =  roba
    
def setRequestedPos_Y(add, roba):
    drone_stringa      = add.split('/')[2]
    iddio              = int(drone_stringa[5:])
    bufferone[iddio].y =  roba

def setRequestedPos_Z(add, roba):
    drone_stringa      = add.split('/')[2]
    iddio              = int(drone_stringa[5:])
    bufferone[iddio].z =  roba

def setRequestedCol_R(address, args):
    drone_stringa      = address.split('/')[2]
    iddio              = int(drone_stringa[5:])
    bufferone[iddio].r= int(args) 

def setRequestedCol_G(address, args):
    drone_stringa      = address.split('/')[2]
    iddio              = int(drone_stringa[5:])
    bufferone[iddio].g= int(args) 

def setRequestedCol_B(address, args):
    drone_stringa      = address.split('/')[2]
    iddio              = int(drone_stringa[5:])
    bufferone[iddio].b= int(args) 
 
def setRequestedTimecode(address, args):
    global timecode
    timecode = int(args)
    # print(args[0])
    # print(args[0])
    if is_automatic:
        if timecode >= lead_IN and not recording and not finished:
            record_routine()
        if timecode >= lead_OUT and recording:
            stop_recorder()
            ciao_ciao()
    
def keyboard_init():
    def nnamo():
        while not finished:
            # print('Press key [combination] (Kill console to quit): ', end='', flush=True)
            key = msvcrt.getwch()
            num = ord(key)
            # print('num: %s'%num)
            # if num in (0, 224):
            #     ext = msvcrt.getwch()
            #     print(f'prefix: {num}   -   key: {ext!r}   -   unicode: {ord(ext)}')
            # else:
            #     print(f'key: {key!r}   -   unicode: {ord(key)}')

            if num == 13 and recording == False:
                record_routine()
            elif num == 13 and recording == True:
                print ('already recording')
            if num == 113 and recording == True:
                stop_recorder()
            elif num == 113 and recording == False:
                print ('not started')
            if num == 3:
                ciao_ciao()
            time.sleep(0.2)
    nn = threading.Thread(target=nnamo).start()
    print("Recording Server started on port %d." % (porta))  
    print("\npress enter to start recording or send a \"/recorder/start 1\" OSC message")  
    print("Press q to terminate and save. Or send a \"/recorder/stop 1\" OSC message")
    print("Press ctrl + c to exit.")

def OSC_init():
    try:
        parser   = argparse.ArgumentParser()
        parser.add_argument("--ip", default="0.0.0.0", help="The ip to listen on")
        parser.add_argument("--port",type=int, default=porta, help="The port to listen on")
        args = parser.parse_args()

        dispatcher = Dispatcher()
        # dispatcher.map("/filter", print)
        # dispatcher.map("/volume", print_volume_handler, "Volume")
        # dispatcher.map("/logvolume", print_compute_handler, "Log volume", math.log)
        dispatcher.map("/notch/drone*/posX", setRequestedPos_X)
        dispatcher.map("/notch/drone*/posZ", setRequestedPos_Y)
        dispatcher.map("/notch/drone*/posY", setRequestedPos_Z)
        dispatcher.map("/notch/drone*/R", setRequestedCol_R)
        dispatcher.map("/notch/drone*/G", setRequestedCol_G)
        dispatcher.map("/notch/drone*/B", setRequestedCol_B)
        dispatcher.map("/notch/timecode", setRequestedTimecode)
        server = osc_server.ThreadingOSCUDPServer( (args.ip, args.port), dispatcher)
        print("Serving on {}".format(server.server_address))
        server.serve_forever()
        time.sleep(1) 
    except Exception as err:
         print(str(err))

    # def OSC_read():
    #     while not finished:
    #         try:
    #             time.sleep(0.0001)
    #             osc_process()      
    #         except KeyboardInterrupt:
    #             print('stopping OSC')
    #             osc_terminate()
    # OSC_thread = threading.Thread(target=OSC_read).start()
 
def record_routine(*args):
    global recording
    def informami():
        while recording:
            print("L\'attuale registrazione ha %s righe. %s" % (righe, math.floor(time.time_ns()/1000000 - tempo_di_inizio)))
            time.sleep(2)

    def salva_una_riga():
        global righe
        if recording:
            il_tempo_dall_inizio = math.floor(time.time_ns()/1000000 - tempo_di_inizio)
            # il_tempo_dall_inizio = math.floor((perf_counter() - tempo_di_inizio)*1000)
            righe += 1
            for drogno in bufferone:
                d = bufferone[drogno] 
                d.records.append( { 'Time' : il_tempo_dall_inizio, 'x' : d.x, 'y' : d.y, 'z' : d.z, 'Red' : d.r, 'Green' : d.g, 'Blue' : d.b })
                # print(f"{drogno=} {il_tempo_dall_inizio=} {d.x=} {d.y=} {d.z=} {d.r=} {d.g=} {d.b=}")
                if drogno==8:
                    print(f"{drogno=}{tab}{il_tempo_dall_inizio=}{tab}{timecode=}{tab}{d.x=}{tab}{d.y=}{tab}{d.z=}{tab}{d.r=}{tab}{d.g=}{tab}{d.b=}")

            
    def ricorda():
        global righe
        global tempo_di_inizio
        tempo_di_inizio      = time.time_ns()/1000000
        data_di_inizio       = datetime.datetime.now()
        dt_string            = data_di_inizio.strftime("%d-%m-%Y_%H-%M-%S")
        nome_registrazione   = 'registrazione_'+dt_string
        cartella_di_questa_registrazione = os.path.join(os.getcwd(),cartella_registrazioni, nome_registrazione)
        
        if not pathlib.Path(cartella_di_questa_registrazione).exists():
            os.mkdir(cartella_di_questa_registrazione)

        print ('Partita la registrazione: %s per %s droni.'% (nome_registrazione, numero_drogni))
        while recording:
            time.sleep(intervallo)
            salva_una_riga()
        print("ho smesso di registrare!")
        righe = 0

        for drogno in bufferone:
            # print ('drogno numero: %s:'% bufferone[drogno].name)
            # print(bufferone[drogno].records)
            bufferone[drogno].df      = pd.DataFrame.from_records(bufferone[drogno].records)
            bufferone[drogno].listone = pd.concat([bufferone[drogno].headers, bufferone[drogno].df])
            # print(bufferone[drogno].listone)
            nomeFile = 'drone_' + str(bufferone[drogno].ID)+'.csv'
            patto = os.path.join(os.getcwd(),cartella_registrazioni, nome_registrazione, nomeFile)
            bufferone[drogno].listone.to_csv(patto, index=False)
        shutil.make_archive(base_name=os.path.join(os.getcwd(),cartella_registrazioni, cartella_di_questa_registrazione), format= 'zip', root_dir=os.path.join(os.getcwd(),cartella_registrazioni, nome_registrazione))
        print('Registrazione %s salvata.'% nome_registrazione)
    if not recording:
        recording = True
        inf  = threading.Thread(target=informami).start()
        ric  = threading.Thread(target=ricorda).start()

def faiIlBufferon():
    global bufferone
    for i in range (0,numero_drogni):
        bufferone[i] = bufferDrone(i)
class bufferDrone():
    def __init__(self, ID ):
        self.ID          = int(ID)
        self.name        = 'bufferDrone'+str(ID)
        self.x           = 0.0
        self.y           = 0.0
        self.z           = 0.0
        self.r           = 0
        self.g           = 0
        self.b           = 0
        self.headers     = pd.DataFrame(columns = ["Time","x", "y", "z", "Red", "Green", "Blue"])
        self.records     = []

def stop_recorder(*args):
    global recording
    if recording:
        print (args)
        print('\nstoppo la registrazione\n')
        recording = False

def ciao_ciao(*args):
    global finished, recording
    recording = False
    finished  = True
    print('Bye bye. \n')
    sys.exit("Putin merda")

if __name__ == '__main__':
    signal.signal(signal.SIGINT, ciao_ciao) ## cattura il control+C e gli fa fare il ciao, ciao 
    faiIlBufferon()
    OSC_init()      
    keyboard_init()
    while not finished:
        time.sleep(1)
        pass
