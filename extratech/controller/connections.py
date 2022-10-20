import time,sys
from   inputimeout import inputimeout, TimeoutOccurred
from   concurrent.futures       import ThreadPoolExecutor
from   cflib.utils.power_switch import PowerSwitch
import cflib.crtp
from   cflib.utils import uri_helper
from   rich import print

import OSCStuff as OSC
import Drogno
import GLOBALS as GB
import common_utils

def radioStart():
    if not GB.WE_ARE_FAKING_IT:
        cflib.crtp.init_drivers()
       

        print('Scanning usb for Crazy radios...')
        radios = cflib.crtp.get_interfaces_status()

        if (radios['radio'] == 'Crazyradio not found'):
            raise Exception("no radio!")
        else:
            print("[bold blue]%s radio trovata:"%len(radios))
            print(radios)
    else: 
        print('simulo di aver trovato una radio')
        time.sleep(1)

def add_crazyflies():
    if GB.WE_ARE_FAKING_IT:
        print('simulo di aver aggiunto i crazifliii')
        time.sleep(1) 
        return

    available_crazyfliess = []
    print('Scanning interfaces for Crazyflies in URI start list')
    if len(GB.uris) > 0:
        for iuro in GB.uris:
            print ('looking for %s ' % iuro)
            available_crazyflies  = cflib.crtp.scan_interfaces(uri_helper.address_from_env(iuro))  ## davvero non ho capito perché sta roba non funzioni
            if available_crazyflies:
                available_crazyfliess.append(available_crazyflies)

    if available_crazyfliess:
        print(f'gente già in giro:')
        print (available_crazyfliess)    
        return available_crazyfliess 

        # for i in available_crazyfliess:
        #     print ('Found %s radios.' % len(available_crazyfliess))
        #     print ("URI: [%s]   ---   name/comment [%s]" % (i[0], i[1]))
    else:
        print('no crazyflies?')
    
def autoReconnect():
    while not GB.threads_exit_event.is_set() :
        time.sleep(GB.RECONNECT_FREQUENCY)
        for drogno in GB.drogni:
            if not GB.drogni[drogno].isKilled:
                print('il drogno %s è sparito, provo a riconnettermi' % GB.drogni[drogno].ID)
                IDToBeRenewed  = GB.drogni[drogno].ID
                uriToBeRenewed = GB.drogni[drogno].link_uri
                del GB.drogni[drogno]
                GB.drogni[IDToBeRenewed] = Drogno.Drogno(IDToBeRenewed, uriToBeRenewed, GB.threads_exit_event, GB.WE_ARE_FAKING_IT, GB.PREFERRED_STARTING_POINTS[IDToBeRenewed], GB.lastRecordPath)
                GB.drogni[IDToBeRenewed].start()

def restart_devices():
    if GB.WE_ARE_FAKING_IT:
        print('se fosse la vita vera ora riavvierei i drogni')
        time.sleep(4)
        return
    is_anyone_there = False
    if not len(GB.uris) == 0:
        is_anyone_there = True
        print('Restarting devices in URI list')
        print('GLOBALS.uris meant to be switched on:')
        print(GB.uris)
        with ThreadPoolExecutor(max_workers = 10) as executor:
            executor.map(restarta, GB.uris, timeout=10)
    else:
        is_anyone_there = True
  
    if len(GB.connected_uris) == 0 or is_anyone_there == False:
        opinion = ('there actually no drognos, wanna retry?\nPress R to retry,\nQ to exit, or S to stand-by. Starting in 3 seconds anyway')
      
        try:
            something = inputimeout(prompt=opinion, timeout=3)
            if opinion == 'r' or opinion == 'R':
                restart_devices()
            if opinion == 's' or opinion == 'S':
                return
            if opinion == 'q' or opinion == 'Q':
                sys.exit()
        except TimeoutOccurred:
            print('Parto, va.')
            return
    else:
        print('at the end these are drognos we have:')
        print(GB.connected_uris)
        print ('aspetto 4 secondi che i CF si sveglino')
        time.sleep(1)
        print('3')
        time.sleep(1)
        print('2')
        time.sleep(1)
        print('1')
        time.sleep(1)

def add_just_one_crazyflie(one_CF_I_am_looking_for):
    print('boom %s' % one_CF_I_am_looking_for)
    if not GB.WE_ARE_FAKING_IT:
        print ('looking for %s ' % one_CF_I_am_looking_for)
        # try:
        #     available_single_CF_I_am_looking_for  = cflib.crtp.scan_interfaces(uri_helper.address_from_env(one_CF_I_am_looking_for))
        #     if available_single_CF_I_am_looking_for:
        #         print('Effettivamente potrei aggiungere: %s' % uri_helper.address_from_env(one_CF_I_am_looking_for))
        #     else:
        #         print('non raggiungo %s' % one_CF_I_am_looking_for)
        # except Exception:
        #         print('%s is unreachable and says %s' % (one_CF_I_am_looking_for, e))    
        try: 
            PowerSwitch(one_CF_I_am_looking_for).stm_power_cycle()
        except Exception:
                print('%s is not there to be shut down' % one_CF_I_am_looking_for)
                # raise Exception
    else: 
        print('simulo di aver aggiunto un crazifliio') 
        time.sleep(1) 
    iddio = common_utils.IDFromURI(one_CF_I_am_looking_for)
    print('provo ad aggiunger il drone con l\'iddio %s ' % iddio)
    time.sleep(3)

    newDrogno = Drogno.Drogno(iddio, one_CF_I_am_looking_for, GB.lastRecordPath)
    GB.drogni[iddio] = newDrogno
    GB.drogni[iddio].start()
    GB.connected_uris.append = one_CF_I_am_looking_for
    print('crazyflie aggiunto')

def create_classes():
    for uro in GB.connected_uris:
        iddio = common_utils.IDFromURI(uro)
        try:
            GB.drogni[iddio] = Drogno.Drogno(iddio, uro, GB.lastRecordPath)
            GB.drogni[iddio].start()
        except Exception as e:
            print (' non ho istanziato %s perché %s' % (uro, e))
        print('drogni avviati')
        print(GB.drogni)

def restarta(urico):
    try: 
        print('spengo %s'% urico)
        PowerSwitch(urico).stm_power_down()

    except Exception:
        print('%s is not there to be shut down' % urico)
    # raise Exception
    time.sleep(0.2)
    
    try:
        print('trying to power up %s' % urico) 
        PowerSwitch(urico).stm_power_up()
        GB.connected_uris.append(urico)

    except Exception: 
        print('%s is not there to be woken up, gonna pop it out from my list' % GB.uris[urico])
        # urisToBeRemoved.append(GB.uris[urico])


