###
### test iniziale:

from tkinter import W
import   pandas                                     as     pd
from     IPython.display                            import display

import   threading
import   pandas
import   time, os, sys, logging
import   wakeUppatore, stenBaiatore
from     pprint                                     import pprint
from     dotenv                                     import load_dotenv

load_dotenv()
CONTROLLER_PATH = os.environ.get('CONTROLLER_PATH')

from     cflib.crazyflie                            import Crazyflie
from     cflib.crazyflie.syncCrazyflie              import SyncCrazyflie
from     cflib.crazyflie.mem                        import MemoryElement
from     cflib.crazyflie.mem                        import Poly4D
from     cflib.utils                                import uri_helper
import   cflib.crtp
from     cflib.crazyflie.log                        import LogConfig
import   DataDrogno  

from   colorama              import Fore, Back, Style
from   colorama              import init as coloInit  
coloInit(convert=True)


available  = []
data_d = {}
# tabellona  = pd.DataFrame(columns=['Drone', 'Motor Pass', 'Battery Sag', 'Battery Test Passed', 'Radio RSSI'])
iddio      = 0
PRINTRATE  = 1
paginegialle = [
    # 'E7E7E7E7E0',
    'E7E7E7E7E1',
    # 'E7E7E7E7E2',
    # 'E7E7E7E7E3',
    # 'E7E7E7E7E4',
    'E7E7E7E7E5',
    'E7E7E7E7E6',
    # 'E7E7E7E7E7',
    'E7E7E7E7E8',
    # 'E7E7E7E7E9'
]

test_completed = False


def scan_for_crazyflies():
    global available
    print(Fore.WHITE + "Scanning for available radios...")
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
        data_d[iddio] = DataDrogno.dataDrone(iddio, uro)
        data_d[iddio].connect()

def IDFromURI(uri) -> int:
    # Get the address part of the uri
        address = uri.rsplit('/', 1)[-1]
        try:
            # print(int(address, 16) - 996028180448)
            return int(address, 16) - 996028180448
        except ValueError:
            print('address is not hexadecimal! (%s)' % address, file=sys.stderr)
            return None

def check_if_test_is_completed():
    
    dataframes = []

    while not (all (data_d[datadrogno].is_testing_over != False for datadrogno in data_d)):
        time.sleep(1)
        
    test_completed = True

    for drogno in data_d:
        # print(data_d[drogno].battery_sag)
        # print(data_d[drogno].battery_voltage)
        # print(data_d[drogno].RSSI)
        i = 0
        dataframe = pd.DataFrame({'Indirizzo'              : [data_d[drogno].link_uri], 
                                  'Battery Sag'            : [data_d[drogno].battery_sag],
                                  'Battery Voltage'        : [data_d[drogno].battery_voltage],
                                  'Battery Test Pass'      : [data_d[drogno].battery_test_passed],
                                  'Propeller Test'         : [data_d[drogno].propeller_test_result],
                                  'Propeller Test Pass'    : [data_d[drogno].propeller_test_passed],
                                  'RSSI'                   : [data_d[drogno].RSSI],
                                  'Revisione Firmware (1)' : [data_d[drogno].firmware_revision0],
                                  'Revisione Firmware (2)' : [data_d[drogno].firmware_revision1]},
                                  index             = ['Drone ' + str(drogno)])
        dataframes.append(dataframe)
        i += 1
    
    df = pd.concat([drogno for drogno in dataframes])
    # df = df.align()
    
    display(df)
    print()
    print('tutti i test sono stati completati')
    time.sleep(3)
    print('metto a ninna tutti... ')
    time.sleep(2)
    for drogno in data_d:
        stenBaiatore.standBySingle(data_d[drogno].link_uri)


def main():
    
    cflib.crtp.init_drivers()

    wakeUppatore.wekappa()

    try:
        scan_for_crazyflies()
    except Exception as e:
        print(".")
    
    

    istanziaClassi()
    # display(tabellona)
    check_if_completed = threading.Thread(target=check_if_test_is_completed).start()

    

if __name__ == '__main__':
    main()
    while not test_completed:
        time.sleep(1)
        pass


















# Initiate the low level drivers

### _routine componi indirizzi completi:   array indirizzi --> array con canali

### _routine connessione  prendi da un pool di thread e provi. 

###  routine esegui test:      prendono istanza da lista drone, fa partire i test e controlla che siano finiti, infine fa partire la stampa
### _test batteria             prendono istanza da lista drone, fa il check, scrive il risultato 

### _test radio (verificare un buon valore)  prendono istanza da lista drone, fa il check, scrive il risultato 

## _funzione stampa             prendono istanza da lista droni presenti - stampa i risultati (e dato riassuntivo)
