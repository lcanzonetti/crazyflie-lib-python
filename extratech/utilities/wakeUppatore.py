#rf 2021
#ciao
import time
#custom modules
from   cflib.utils.power_switch import PowerSwitch
from   colorama              import Fore, Back, Style
from   colorama              import init as coloInit  
coloInit(convert=True)


uris = [    
        # 'radio://0/80/2M/E7E7E7E7E0',
        'radio://0/80/2M/E7E7E7E7E1',
        # 'radio://0/80/2M/E7E7E7E7E2',
        # 'radio://1/90/2M/E7E7E7E7E3',
        # 'radio://1/90/2M/E7E7E7E7E4',
        # 'radio://1/90/2M/E7E7E7E7E5',
        # 'radio://2/100/2M/E7E7E7E7E6',
        # 'radio://2/100/2M/E7E7E7E7E7',
        # 'radio://2/100/2M/E7E7E7E7E8',
        # 'radio://3/110/2M/E7E7E7E7E9',
        # 'radio://0/110/2M/E7E7E7E7EA',
        ]
 
 
def main():
    print('Waking up devices')
    for uri in uris:
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
    main()

