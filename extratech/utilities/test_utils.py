############    Generic Imports
import   pandas                                               as     pd
from     colorama              import Fore, Back, Style
from     datetime                                             import datetime
from     IPython.display                                      import display
import   time, os, sys, signal, threading, importlib, subprocess

############    Local Imports
from     common_utils                                         import IDFromURI
import   GLOBALS                                              as     GB
from     flash_util                                           import flasha_firmware_subprocess
from common_utils import write
# import   GUI

############    Environment Imports
from     dotenv                                               import load_dotenv
load_dotenv()

############    CrazyFlie Imports
import cflib
import cflib.crtp

import   wakeUppatore, stenBaiatore, DataDrogno

def misaidirelora():
    oggieora   = str(datetime.now())                                              ### Crea stringa in formato yyyymmddhhmmss per creazione nome json
    oggieora   = oggieora.replace('-', '')
    oggieora   = oggieora.replace(' ', '')
    oggieora   = oggieora.replace(':', '')
    oggieora   = oggieora[:-7]
    return oggieora

is_test_completed = False

def istanziaClassi():
    # cancellami = DataDrogno.dataDrone(IDFromURI('E7E7E7E7E1'),'E7E7E7E7E1')
    for uro in GB.available:
        iddio = IDFromURI(uro)
        GB.data_d[iddio] = DataDrogno.dataDrone(iddio, uro)
        GB.data_d[iddio].connect()

def scan_for_crazyflies():
    GB.available.clear()
    write(GB.available)
    write("Scanning for available radios...")
    for i in GB.paginegialle:
        GB.available.append(cflib.crtp.scan_interfaces(address=int(i, 16)))
    GB.available = list(filter(None, GB.available))
    GB.available = [x[0] for x in GB.available]
    GB.available = [x[0] for x in GB.available]
    write("\nTrovate %s radio!" %(len(GB.available)))
    for i in GB.available:
        write(i)
    write("\n")
    return GB.available

def write_json(location):
    dati_mech = []
    dati_rev = []
    def thread_json():
        for drogno in GB.data_d:
            i = 0
            if GB.data_d[drogno].battery_sag == 0: 
                batt_sag = 'Not Tested'
                batt_test_passed = 'Not Tested'
            else: 
                batt_sag = GB.data_d[drogno].battery_sag
                batt_test_passed = GB.data_d[drogno].battery_test_passed
            if GB.data_d[drogno].propeller_test_result == [0,0,0,0]:
                prop_test_result = GB.data_d[drogno].propeller_test_result
                prop_test_passed = 'Not passed, but probably not tested. Could all the motors possibly have failed?'
            else: 
                prop_test_result = GB.data_d[drogno].propeller_test_result
                prop_test_passed = GB.data_d[drogno].propeller_test_passed
            if GB.data_d[drogno].bandwidth == None:
                bandwidth_0 = 0
                bandwidth_1 = 0
                latency = 0
            else:
                bandwidth_0 = GB.data_d[drogno].bandwidth[0]
                bandwidth_1 = GB.data_d[drogno].bandwidth[1]
                latency = GB.data_d[drogno].latency


            data_mech = pd.DataFrame({'Indirizzo'            : [GB.data_d[drogno].link_uri], 
                                    'Battery Sag'            : [batt_sag],
                                    'Battery Voltage'        : [GB.data_d[drogno].battery_voltage],
                                    'Battery Test Pass'      : [batt_test_passed],
                                    'Propeller Test'         : [prop_test_result],
                                    'Propeller Test Pass'    : [prop_test_passed],
                                    'RSSI'                   : [GB.data_d[drogno].RSSI],
                                    'Bandwidth'              : ['%s pkg/s %s kB/s' %(float("{:.2f}".format(bandwidth_0)), float("{:.2f}".format(bandwidth_1)))],
                                    'Latency'                : ['%s ms' %float("{:.2f}".format(latency))]},
                                    index                    = ['Drone ' + str(drogno)])
            dati_mech.append(data_mech)
            data_rev = pd.DataFrame({'Revisione Firmware (1)' : [GB.data_d[drogno].firmware_revision0],
                                     'Revisione Firmware (2)' : [GB.data_d[drogno].firmware_revision1]},
                                     index                    = ['Drone ' + str(drogno)])
            dati_rev.append(data_rev)
            i += 1
        try:
            df1 = pd.concat([drogno for drogno in dati_mech])
            df2 = pd.concat([drogno for drogno in dati_rev])
            display(df1)
            # write("\n")
            display(df2)
            df1.to_json(location + '/Test_Resultsss/Risultati_mech_' + misaidirelora() + '.json', orient='index', indent=4)         ### Scrive un file json con i risultati
            df2.to_json(location + '/Test_resultsss/Risultati_rev_'  + misaidirelora() + '.json', orient='index', indent=4)
        except ValueError:
            write('mi sa che \'sto test è ito buco')
            # sys.exit(0)
            os._exit(0)
            return
    threading.Thread(target=thread_json).start()

def check_if_test_is_completed():
    def thread_if_test_is_completed():
        dati_mech = []                              ### Dati "elettromeccanici" dei droni
        dati_rev  = []                              ### Dati sulla "revisione del firmware"

    

        while not (all (GB.data_d[datadrogno].is_testing_over != False for datadrogno in GB.data_d)):
            time.sleep(1)
            # write('controllo il test... %s' %dati_mech)
        is_test_completed = True

        # user_interface = GUI.Interface()
        # ui_thread = threading.Thread(target = user_interface)
        # ui_thread.start()
            

        for drogno in GB.data_d:
            i = 0
            data_mech = pd.DataFrame({'Indirizzo'            : [GB.data_d[drogno].link_uri], 
                                    'Battery Sag'            : [GB.data_d[drogno].battery_sag],
                                    'Battery Voltage'        : [GB.data_d[drogno].battery_voltage],
                                    'Battery Test Pass'      : [GB.data_d[drogno].battery_test_passed],
                                    'Propeller Test'         : [GB.data_d[drogno].propeller_test_result],
                                    'Propeller Test Pass'    : [GB.data_d[drogno].propeller_test_passed],
                                    'RSSI'                   : [GB.data_d[drogno].RSSI],
                                    'Bandwidth'              : ['%s pkg/s %s kB/s' %(float("{:.2f}".format(GB.data_d[drogno].bandwidth[0])), float("{:.2f}".format(GB.data_d[drogno].bandwidth[1])))],
                                    'Latency'                : ['%s ms' %float("{:.2f}".format(GB.data_d[drogno].latency))]},
                                    index                    = ['Drone ' + str(drogno)])
            dati_mech.append(data_mech)
            data_rev = pd.DataFrame({'Revisione Firmware (1)' : [GB.data_d[drogno].firmware_revision0],
                                     'Revisione Firmware (2)' : [GB.data_d[drogno].firmware_revision1]},
                                     index                    = ['Drone ' + str(drogno)])
            dati_rev.append(data_rev)
            i += 1
        try:
            df1 = pd.concat([drogno for drogno in dati_mech])
            df2 = pd.concat([drogno for drogno in dati_rev])
            display(df1)
            write()
            display(df2)
            df1.to_json(sys.path[5] + '/Test_Resultsss/Risultati_mech_' + misaidirelora() + '.json', orient='index', indent=4)         ### Scrive un file json con i risultati
            df2.to_json(sys.path[5] + '/Test_resultsss/Risultati_rev_'  + misaidirelora() + '.json', orient='index', indent=4)
            # df = df.align()
            write()
            write('tutti i test sono stati completati')
            time.sleep(2)
            

            ### Aspetta finché il LED di ogni drone non ha finito di "lampeggiare"
            while not (all(GB.data_d[drogno].lampeggio_finito for drogno in GB.data_d)):
                # write("il lampeggio non è ancora finito...")
                time.sleep(0.5)
            
            # flasha_firmware_subprocess()
            
            
            write('addormento tutti... ')
            for drogno in GB.data_d:
                stenBaiatore.standBySingle(GB.data_d[drogno].link_uri)
            
            for drogno in GB.data_d:
                GB.data_d[drogno].close_link()
            
            subprocess.call(["python", "flash_util.py"],cwd = "C:/Users/produ/Documents/GITHUB_REPOS/crazyflie-lib-python/extratech/utilities")

        except ValueError:
            write('mi sa che \'sto test è ito buco')
            # sys.exit(0)
            os._exit(0)
            return
    threading.Thread(target=thread_if_test_is_completed).start()
