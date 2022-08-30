#rf 2021
#ciao
import time
#custom modules
from   cflib.utils.power_switch import PowerSwitch
from   colorama              import Fore, Back, Style
from   colorama              import init as coloInit  
coloInit(convert=True)

droni = 8
radio = 1
import cflib.crtp

# Initiate the low level drivers
def cercaya():
    cflib.crtp.init_drivers()

    print('Scanning interfaces for Crazyflies...')
    available = cflib.crtp.scan_interfaces() 
    cflib.crtp.scan_interfaces()
    print('Crazyflies found:')
    for i in available:
        print(i[0])


def stenbaya():
    print ("creating CF list")
    uris = create_CF_list(droni, radio)
    print('StandBying devices')
    for uri in uris:
        try:
            PowerSwitch(uri).stm_power_down()
            print(Fore.GREEN + '%s has been standbyied!' % uri)
        except Exception:
            print(Fore.RED + '%s is not there to be standByied' % uri)
    time.sleep(1)
    print ('Done. Ciao.')

def standBySingle(uri):
    print(Fore.WHITE + 'StandBying device %s' % uri)
    try:
        PowerSwitch(uri).stm_power_down()
        print(Fore.GREEN + '%s has been standbyied!' % uri)
    except Exception:
        print(Fore.RED + '%s is not there to be standByied' % uri)
 
def create_CF_list(numero_massimo_droni = 10, radio_installate = 1):
    canali_radio = [80, 90, 100]
    list = []
    numero = 996028180448   ## E7E7E7E7E0
    for drone_potenziale in range (numero, numero + numero_massimo_droni):
        for canale in canali_radio:
            for radio in range(radio_installate):
                esadecimalato = str(hex(drone_potenziale)).upper().lstrip()
                list.append(f'radio://{radio}/{canale}/2M/{esadecimalato[2:]}')
    return list

def create_CF_list_address_only(numero_massimo_droni = 10, radio_installate = 1):
    canali_radio = [80, 90, 100]
    list = []
    numero = 996028180448   ## E7E7E7E7E0
    for drone_potenziale in range (numero, numero + numero_massimo_droni):
        for canale in canali_radio:
            for radio in range(radio_installate):
                esadecimalato = str(hex(drone_potenziale)).upper().lstrip()
                list.append(hex(drone_potenziale))
    return list

if __name__ == '__main__':
    # stenbaya()
    cercaya()