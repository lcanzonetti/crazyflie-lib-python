###
### test iniziale:
import time, os, sys, logging 
from   pprint import pprint
from   dotenv import load_dotenv
load_dotenv()
CONTROLLER_PATH = os.environ.get('CONTROLLER_PATH')
from   cflib.crazyflie                            import Crazyflie
from   cflib.crazyflie.syncCrazyflie              import SyncCrazyflie
from   cflib.crazyflie.mem                        import MemoryElement
from   cflib.crazyflie.mem                        import Poly4D
from   cflib.utils                                import uri_helper
import cflib.crtp
from   cflib.crazyflie.log                        import LogConfig


import   DataDrogno  

available  = []
drogni     = {}
datadrogni = {}
iddio      = 0
PRINTRATE  = 1
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


def scan_for_crazyflies():
    global available
    print("Scanning for available radios...")
    for i in paginegialle:
        available.extend(cflib.crtp.scan_interfaces(address=int(i, 16)))
    
    available = list(filter(None, available))
    available = [x[0] for x in available]

    print("\nTrovate %s radio!" %(len(available)))
    for i in available:
        print(i)
    print("\n")

    return available

def istanziaClassi():
    for uro in available:
        iddio = IDFromURI(uro)
        print(uro)
        datadrogni[iddio] = DataDrogno.dataDrone(iddio, uro)
        DataDrogno.dataDrone()
        datadrogni[iddio].connectToEverything()

def IDFromURI(uri) -> int:
    # Get the address part of the uri
        address = uri.rsplit('/', 1)[-1]
        try:
            # print(int(address, 16) - 996028180448)
            return int(address, 16) - 996028180448
        except ValueError:
            print('address is not hexadecimal! (%s)' % address, file=sys.stderr)
            return None

def closeAllLinks():
    for i in drogni:
        drogni[i].close_link()
        print("Ora chiudo con %s" %(i))


def main():
    cflib.crtp.init_drivers()
    time.sleep(2)
    try:
        scan_for_crazyflies()
    except Exception as e:
        print(".")
    istanziaClassi()
    closeAllLinks()

if __name__ == '__main__':
    main()


















# Initiate the low level drivers

### _routine componi indirizzi completi:   array indirizzi --> array con canali

### _routine connessione  prendi da un pool di thread e provi. 

###  routine esegui test:      prendono istanza da lista drone, fa partire i test e controlla che siano finiti, infine fa partire la stampa
### _test batteria             prendono istanza da lista drone, fa il check, scrive il risultato 

### _test radio (verificare un buon valore)  prendono istanza da lista drone, fa il check, scrive il risultato 

## _funzione stampa             prendono istanza da lista droni presenti - stampa i risultati (e dato riassuntivo)
