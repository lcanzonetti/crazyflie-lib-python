#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#rf 2023

import time, sys, threading, logging, signal, math, datetime, os, pathlib
from itertools import cycle
from   osc4py3.as_eventloop  import *
from   osc4py3               import oscmethod as osm
from   osc4py3               import oscbuildparse
import pandas as pd
from time import perf_counter
from timeloop import Timeloop
from datetime import timedelta
tl = Timeloop()

nowa                 = datetime.datetime.now()
dt_string            = nowa.strftime("%d-%m-%Y_%H-%M-%S")
registrazione        = 'registrazione_'+dt_string
nomeRegistrazione    = pathlib.Path(registrazione).stem

print (nomeRegistrazione)
OUTPUT_DIR           = 'registrazioniOSC'
if not pathlib.Path(OUTPUT_DIR).exists():
  os.mkdir(OUTPUT_DIR)
os.chdir(OUTPUT_DIR)
if not pathlib.Path(nomeRegistrazione).exists():
  os.mkdir(nomeRegistrazione)
os.chdir('..')

drogni            = 10
intervallo        = 0.04
porta             = 9200


loop              = cycle(r"-\|/")
bufferone         = {}
timecode          = '00:00:00:00'
start_time        = 0
finished          = False

def runnnn():
    print("running ...", next(loop), end='\r', flush=True)

def setRequestedPos(address, args):
    global timecode
    x = address.split('/')
    y = x[2].split('_')
    iddio = int(y[1])
    print('Ciao sono il drone %s e dovrei andare a X %s, Y %s, Z %s' %(iddio,round(float(args[0]),3), round(float(args[1]),3), round(float(args[2]),3)))

    bufferone[iddio].x = round(float(args[0]),3)
    bufferone[iddio].y = round(float(args[1]),3)
    bufferone[iddio].z = round(float(args[2]),3)
    
def setRequestedCol(address, args):
    x = address.split('/')
    y = x[2].split('_')
    iddio = int(y[1])

    bufferone[iddio].r = args[0]
    bufferone[iddio].g = args[1]
    bufferone[iddio].b = args[2]
    print('Ciao sono il drone %s e dovrei avere il colore R %s, G %s, B %s' %(iddio, args[0],  args[1], args[2] ))

def recorda():
    try:
        input("press enter to start recording and q to stop")
        # logging.basicConfig(format='%(asctime)s - %(threadName)s ø %(name)s - '  '%(levelname)s - %(message)s')
        # logger = logging.getLogger("osc")
        # logger.setLevel(logging.DEBUG)
        # osc_startup(logger=logger)
        osc_startup()
        osc_udp_server("0.0.0.0", porta,   "receivingServer")
        ###########################  single fella requested position
        osc_method("/notch/drone*/pos",   setRequestedPos,      argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)
        osc_method("/notch/drone*/col",   setRequestedCol,      argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)
        # print("Recording Server started on port %d. Press q terminate and save." % (porta))
    except Exception as err:
         print(str(err))
    while not finished:
        try:
            time.sleep(0.05)
            runnnn()
            osc_process()
            
        except KeyboardInterrupt:
            print('Recording Done')
            osc_terminate()
            sys.exit()
 
def faiIlBufferon():
    global bufferone
    for i in range (0,drogni):
        bufferone[i] = bufferDrone(i)

def quando_passa_il_tempo_mettiamo_una_linea():

    def salva_una_riga():
        il_tempo_dall_inizio = math.floor((perf_counter() - start_time)*1000)
        for drogno in bufferone:
            d = bufferone[drogno] 
            d.records.append( { 'Time' : il_tempo_dall_inizio, 'x' : d.x, 'y' : d.y, 'z' : d.z, 'Red' : d.r, 'Green' : d.g, 'Blue' : d.b })
            # print(f"{il_tempo_dall_inizio=}, {d.x=}")
    def conta():
        print("comincio a registrare!")
        while not finished:
            time.sleep(intervallo)
            # il_tempo_dall_inizio = math.floor(start_time - (time.time()*1000))
            # print (f"{il_tempo_dall_inizio=}")
            # if ( il_tempo_dall_inizio % intervallo) == 0:
            salva_una_riga()
        print("ho smesso di registrare!")
    cc = threading.Thread(target=conta).start()

class bufferDrone():
    def __init__(self, ID ):
        self.ID          = int(ID)
        self.name        = 'bufferDrone'+str(ID)
        self.x           = 0.0
        self.y           = 0.0
        self.z           = 1.0
        self.r           = 0
        self.g           = 0
        self.b           = 0
        self.headers     = pd.DataFrame(columns = ["Time","x", "y", "z", "Red", "Green", "Blue"])
        self.records     = []
        
def ciao_ciao(signum, frame):
    global finished
    print('Bye bye. \n%s' % signum)
    finished = True
    time.sleep(1)
       

    for drogno in bufferone:
        print ('drogno numero: %s:'% bufferone[drogno].name)
        # print(bufferone[drogno].records)
        bufferone[drogno].df      = pd.DataFrame.from_records(bufferone[drogno].records)
        bufferone[drogno].listone = pd.concat([bufferone[drogno].headers, bufferone[drogno].df])
        print(bufferone[drogno].listone)

        nomeFile = 'drone_' + str(bufferone[drogno].ID)+'.csv'
        print (OUTPUT_DIR)
        print (nomeRegistrazione)
        print (nomeFile)
        patto = os.path.join(os.getcwd(),OUTPUT_DIR, nomeRegistrazione, nomeFile)
        print (patto)
        bufferone[drogno].listone.to_csv(patto, index=False)
        
    sys.exit("Putin merda")

if __name__ == '__main__':
    signal.signal(signal.SIGINT, ciao_ciao) ## cattura il control+C e gli fa fare il ciao, ciao 
    faiIlBufferon()
    start_time = perf_counter()
    OSCRefreshThread      = threading.Thread(target=recorda).start()
    
    quando_passa_il_tempo_mettiamo_una_linea()
  
    while not finished:
        time.sleep(0.1)
        pass
