#rf 2021
#ciao
import time

#custom modules
from stenBaiatore import create_CF_list
#cf modules
from   cflib.utils.power_switch import PowerSwitch
from   colorama              import Fore, Back, Style
from   colorama              import init as coloInit  
coloInit(convert=True)

droni = 8
radio = 1

def wekappa():
    print('Waking up devices')
    for uri in create_CF_list(droni, radio):
        try:
            PowerSwitch(uri).stm_power_up()
            print(Fore.GREEN + '%s has been woke upped!' % uri)
        except Exception:
            print(Fore.RED + '%s is not there to be woke up' % uri)
    time.sleep(1)
    print ('Done. Ciao.')

def wakeUpSingle(uri):
    print('Waking up device %s' % uri)
    try:
        PowerSwitch(uri).stm_power_up()
        print(Fore.GREEN + '%s has been woke upped!' % uri)
    except Exception:
        print(Fore.RED + '%s is not there to be woke up' % uri)
 
if __name__ == '__main__':
    wekappa()

