import time,sys,threading,multiprocessing
import OSCStuff as OSC

import GUI
import Drogno
import GLOBALS
from   GLOBALS import PREFERRED_STARTING_POINTS as PFS



from   cflib.utils.power_switch import PowerSwitch
import cflib.crtp
from   cflib.utils import uri_helper

lastRecordPath        = ''  

threads_exit_event   = processes_exit_event = None
drogni = {}
WE_ARE_FAKING_IT = GLOBALS.WE_ARE_FAKING_IT

def add_just_one_crazyflie(one_CF_I_am_looking_for):
    print('boom %s' % one_CF_I_am_looking_for)
    if not WE_ARE_FAKING_IT:
        print ('looking for %s ' % one_CF_I_am_looking_for)
        available_single_CF_I_am_looking_for  = cflib.crtp.scan_interfaces(uri_helper.address_from_env(one_CF_I_am_looking_for))
        if available_single_CF_I_am_looking_for:
            print(f'Effettivamente potrei aggiungere: ' + one_CF_I_am_looking_for)
        else:
            print('non credo potrò aggiungere ' + one_CF_I_am_looking_for)
        try: 
            PowerSwitch(one_CF_I_am_looking_for).stm_power_cycle()
        except Exception:
                print('%s is not there to be shut down' % one_CF_I_am_looking_for)
                # raise Exception
    else: 
        print('simulo di aver aggiunto un crazifliio') 
        time.sleep(1) 
    iddio = IDFromURI(one_CF_I_am_looking_for)
    print('provo ad aggiunger il drone con l\'iddio %s ' % iddio)
    newDrogno = Drogno.Drogno(iddio, one_CF_I_am_looking_for, threads_exit_event, processes_exit_event, WE_ARE_FAKING_IT, PFS[iddio], lastRecordPath)
    drogni[iddio] = newDrogno
    drogni[iddio].start()
    print('crazyflie aggiunto')

    # send drogni's array to submodules
    OSC.drogni[iddio] = newDrogno
    GUI.drogni[iddio] = newDrogno


def IDFromURI(uri):
    # Get the address part of the uri
    address = uri.rsplit('/', 1)[-1]
    try:
        # print(int(address, 16) - 996028180448)
        return int(address, 16) - 996028180448
    except ValueError:
        print('address is not hexadecimal! (%s)' % address, file=sys.stderr)
        return None