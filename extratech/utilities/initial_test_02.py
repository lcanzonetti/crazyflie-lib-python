###
### test iniziale:

import   pandas                                     as     pd
from     IPython.display                            import display          ### Serve per "stampare" il DataFrame contenente i risultati
from     datetime                                   import datetime

import   threading
import   time, os, sys, signal
import   wakeUppatore, stenBaiatore
from     dotenv                                     import load_dotenv
load_dotenv()
CONTROLLER_PATH = os.environ.get('CONTROLLER_PATH')

isExist = os.path.exists(sys.path[0] + '/Test_Resultsss')                   ### Chekka se esiste cartella dove scrivere json dei risultati, se no la crea
if not isExist: os.makedirs(sys.path[0] + '/Test_Resultsss')

oggieora = str(datetime.now())                                              ### Crea stringa in formato yyyymmddhhmmss per creazione nome json
oggieora = oggieora.replace('-', '')
oggieora = oggieora.replace(' ', '')
oggieora = oggieora.replace(':', '')
oggieora = oggieora[:-7]
# print(oggieora)

from     cflib.crazyflie                            import Crazyflie
from     cflib.crazyflie.syncCrazyflie              import SyncCrazyflie
from     cflib.crazyflie.mem                        import MemoryElement
from     cflib.crazyflie.mem                        import Poly4D
from     cflib.utils                                import uri_helper
import   cflib.crtp
from     cflib.crazyflie.log                        import LogConfig
from     cflib.utils.power_switch import PowerSwitch

import   DataDrogno  

from   colorama              import Fore, Back, Style
from   colorama              import init as coloInit  
coloInit(convert=True)

available  = []
data_d = {}
iddio      = 0
PRINTRATE  = 1
paginegialle = [
    # 'E7E7E7E7E0',
    'E7E7E7E7E1',
    # 'E7E7E7E7E2',
    'E7E7E7E7E3',
    # 'E7E7E7E7E4',
    # 'E7E7E7E7E5',
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
            return int(address, 16) - 996028180448
        except ValueError:
            print('address is not hexadecimal! (%s)' % address, file=sys.stderr)
            return None

def check_if_test_is_completed():
    dati_mech = []                              ### Dati "elettromeccanici" dei droni
    dati_rev  = []                              ### Dati sulla "revisione del firmware"
    while not (all (data_d[datadrogno].is_testing_over != False for datadrogno in data_d)):
        time.sleep(1)
    test_completed = True
    for drogno in data_d:
        i = 0
        data_mech = pd.DataFrame({'Indirizzo'              : [data_d[drogno].link_uri], 
                                  'Battery Sag'            : [data_d[drogno].battery_sag],
                                  'Battery Voltage'        : [data_d[drogno].battery_voltage],
                                  'Battery Test Pass'      : [data_d[drogno].battery_test_passed],
                                  'Propeller Test'         : [data_d[drogno].propeller_test_result],
                                  'Propeller Test Pass'    : [data_d[drogno].propeller_test_passed],
                                  'RSSI'                   : [data_d[drogno].RSSI],},
                                  index                    = ['Drone ' + str(drogno)])
        dati_mech.append(data_mech)
        data_rev = pd.DataFrame({'Revisione Firmware (1)' : [data_d[drogno].firmware_revision0],
                                 'Revisione Firmware (2)' : [data_d[drogno].firmware_revision1]},
                                  index                   = ['Drone ' + str(drogno)])
        dati_rev.append(data_rev)
        i += 1
    try:
        df1 = pd.concat([drogno for drogno in dati_mech])
        df2 = pd.concat([drogno for drogno in dati_rev])
        display(df1)
        print()
        display(df2)
        df1.to_json(sys.path[0] + '/Test_Resultsss/Risultati_mech_' + oggieora + '.json', orient='index', indent=4)         ### Scrive un file json con i risultati
        df2.to_json(sys.path[0] + '/Test_resultsss/Risultati_rev_' + oggieora + '.json', orient='index', indent=4)
        # df = df.align()
        print()
        print('tutti i test sono stati completati')
        time.sleep(2)
        print('sto per mettere a ninna tutti...')

        ### Aspetta finché il LED di ogni drone non ha finito di "lampeggiare"
        while not (all(data_d[drogno].lampeggio_finito for drogno in data_d)):
            time.sleep(0.5)
        print('addormento tutti... ')
        for drogno in data_d:
            stenBaiatore.standBySingle(data_d[drogno].link_uri)
    except ValueError:
        print('mi sa che \'sto test è ito buco')
        # sys.exit(0)
        os._exit(0)
        return

def exit_signal_handler(signum, frame):
    print('\nEsco.')
    # threads_exit_event.set() 

    for drogno in data_d:
        try: PowerSwitch(data_d[drogno].link_uri).stm_power_down()
        except Exception: print('While closing the program I wanted to shut down %s, which is unfortunately not there to be shut down' % data_d[drogno].link_uri)
    os._exit(0)
    sys.exit(0)

def main():
    cflib.crtp.init_drivers()
    wakeUppatore.wekappa()
    
    try:
        scan_for_crazyflies()
    except Exception as e:
        print(".")
    signal.signal(signal.SIGINT, exit_signal_handler)
    
    istanziaClassi()
    check_if_completed = threading.Thread(target=check_if_test_is_completed).start()

if __name__ == '__main__':
    try:
        main()
        while not test_completed:
            time.sleep(1)
            pass
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    
  


















# Initiate the low level drivers

### _routine componi indirizzi completi:   array indirizzi --> array con canali

### _routine connessione  prendi da un pool di thread e provi. 

###  routine esegui test:      prendono istanza da lista drone, fa partire i test e controlla che siano finiti, infine fa partire la stampa
### _test batteria             prendono istanza da lista drone, fa il check, scrive il risultato 

### _test radio (verificare un buon valore)  prendono istanza da lista drone, fa il check, scrive il risultato 

## _funzione stampa             prendono istanza da lista droni presenti - stampa i risultati (e dato riassuntivo)
