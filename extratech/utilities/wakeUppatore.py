#rf 2021
#ciao
import time
import GLOBALS as GB

#custom modules
from stenBaiatore import create_CF_list

#cf modules
from   cflib.utils.power_switch import PowerSwitch
from   colorama              import Fore, Back, Style
from   colorama              import init as coloInit  
from   common_utils          import write

coloInit(convert=True)

droni = GB.numero_droni
radio = 1

def wekappa():
    GB.available = []
    write('Waking up devices')
    for uri in create_CF_list(droni, radio):
        try:
            PowerSwitch(uri).stm_power_up()
            write('%s has been woke upped!' % uri)
            GB.available.append(uri)
        except Exception:
            write('%s is not there to be woke up' % uri)
        time.sleep(1)
    write ('Done. Ciao.')

def wakeUpSingle(uri):
    write('Waking up device %s' % uri)
    try:
        PowerSwitch(uri).stm_power_up()
        write('%s has been woke upped!' % uri)

    except Exception:
        write('%s is not there to be woke up' % uri)
    time.sleep(1)
    write("Svegliati!")
if __name__ == '__main__':
    wekappa()

