###
### test iniziale:


import time
import sys

import logging
from   pprint import pprint
from   cflib.crazyflie                            import Crazyflie
from   cflib.crazyflie.syncCrazyflie              import SyncCrazyflie
from   cflib.utils                                import uri_helper
import cflib.crtp
from   cflib.crazyflie.log                        import LogConfig

# import simpleDrogno

available = []

drogni = {}

paginegialle = [
    'E7E7E7E7E0',
    'E7E7E7E7E1',
    'E7E7E7E7E2',
    'E7E7E7E7E3',
    'E7E7E7E7E4',
    'E7E7E7E7E5',
    'E7E7E7E7E6',
    'E7E7E7E7E7',
    'E7E7E7E7E8',
    'E7E7E7E7E9'
]

def IDFromURI(uri) -> int:
    # Get the address part of the uri
    address = uri.rsplit('/', 1)[-1]
    try:
        # print(int(address, 16) - 996028180448)
        return int(address, 16) - 996028180448
    except ValueError:
        print('address is not hexadecimal! (%s)' % address, file=sys.stderr)
        return None

### _routine componi indirizzi --> array indirizzi

def scanEverything():
    global available
    print("Scanning for available radios...")
    for i in paginegialle:
        
        available.extend(cflib.crtp.scan_interfaces(address=int(i, 16)))
    
    available = list(filter(None, available))
    available = [x[0] for x in available]

    print("Trovate %s radio!" %(len(available)))
    time.sleep(1)
    for i in available:
        print(i)

    return available

### _routine connetti droni  array con canali --> connessione  --> istanzia classe drogno presente e lista droni presenti

def connectToEverything():
    global available
    
    for uro in available:
        iddio = IDFromURI(uro)
        drogni[iddio] = Drogno.Drogno(iddio, uro, threads_exit_event, processes_exit_event, WE_ARE_FAKING_IT, PREFERRED_STARTING_POINTS[iddio], lastRecordPath)
        drogni[iddio].open_link(uro)
        drogni[iddio]._lg_kalm = LogConfig(name='Stabilizer', period_in_ms=100)
        drogni[iddio]._lg_kalm.add_variable('health.motorPass', 'uint8_t')
        print("Mi sono connesso al drone %s all'indirizzo %s" %(iddio, uro))
        # print("Questi sono tutti i droni che abbiamo %s" %(drogni))

#def printStatus():


def propellerTest():
    print("Inizio Propeller Test... ")
    for drogno in drogni:
        print("Propeller Test per il Drone %s" %(drogno))
        drogni[drogno].param.request_update_of_all_params()
        time.sleep(2)
        drogni[drogno].param.set_value('health.startPropTest', '1')
        time.sleep(3)

def closeAllLinks():

    for i in drogni:
        drogni[i].close_link()
        print("Ora chiudo con %s" %(i))

# Initiate the low level drivers
cflib.crtp.init_drivers()


scanEverything()
connectToEverything()
propellerTest()
closeAllLinks()

### _routine componi indirizzi completi:   array indirizzi --> array con canali

### _routine connessione  prendi da un pool di thread e provi. 

###  routine esegui test:      prendono istanza da lista drone, fa partire i test e controlla che siano finiti, infine fa partire la stampa
### _test batteria             prendono istanza da lista drone, fa il check, scrive il risultato 
### _test propellers           prendono istanza da lista drone, fa il check, scrive il risultato 
### _test radio (verificare un buon valore)  prendono istanza da lista drone, fa il check, scrive il risultato 

## _funzione stampa             prendono istanza da lista droni presenti - stampa i risultati (e dato riassuntivo)



class dataDrone():
    def __init__(self, ID, ):
        self.ID          = int(ID)
        self.name        = 'bufferDrone'+str(ID)
        self.requested_X            = 0.0
        self.requested_Y            = 0.0
        self.requested_Z            = 1.0
        self.requested_R            = 0
        self.requested_G            = 0
        self.requested_B            = 0
        self.yaw                   = 0.0