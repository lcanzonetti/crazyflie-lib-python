#rf 2021
#ciao
import time
#custom modules
from   cflib.utils.power_switch import PowerSwitch

uris = [    
        'radio://0/80/2M/E7E7E7E7E0',
        'radio://0/80/2M/E7E7E7E7E1',
        'radio://0/80/2M/E7E7E7E7E2',
        'radio://1/90/2M/E7E7E7E7E3',
        'radio://1/90/2M/E7E7E7E7E4',
        'radio://1/90/2M/E7E7E7E7E5',
        'radio://2/100/2M/E7E7E7E7E6',
        'radio://2/100/2M/E7E7E7E7E7',
        'radio://2/100/2M/E7E7E7E7E8',
        'radio://3/110/2M/E7E7E7E7E9',
        # 'radio://0/110/2M/E7E7E7E7EA',
        ]
 
 
def main():
    print('StandBying devices')
    for uri in uris:
        try:
            PowerSwitch(uri).stm_power_down()
            print('%s has been standbyied!' % uri)
        except Exception:
            print('%s is not there to be standByied' % uri)
    time.sleep(1)
    print ('Done. Ciao.')
 
if __name__ == '__main__':
    main()

