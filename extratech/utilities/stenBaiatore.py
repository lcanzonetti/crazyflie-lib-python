#rf 2021
#ciao
import time
#custom modules
from   cflib.utils.power_switch import PowerSwitch
from   colorama              import Fore, Back, Style
from   colorama              import init as coloInit  
coloInit(convert=True)

droni = 20
radio = 2
 
def main():
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
    print('StandBying device %s' % uri)
    try:
        PowerSwitch(uri).stm_power_down()
        print(Fore.GREEN + '%s has been standbyied!' % uri)
    except Exception:
        print(Fore.RED + '%s is not there to be standByied' % uri)
 
if __name__ == '__main__':
    main()

def create_CF_list(numero_massimo_droni = 20, radio_installate = 2):
    canali_radio = [80, 100, 110, 120]
    list = []
    numero = 996028180448   ## E7E7E7E7E0
    for drone_potenziale in range (numero, numero + numero_massimo_droni):
        for canale in canali_radio:
            for radio in range(radio_installate):
                esadecimalato = hex(drone_potenziale)
                list.append(f'radio://{radio}//{canale}//{esadecimalato}')
    return list
