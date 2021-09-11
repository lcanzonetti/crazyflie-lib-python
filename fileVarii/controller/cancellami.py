import time

uris = [    
        'radio://0/80/2M/E7E7E7E7E0',
        'radio://0/80/2M/E7E7E7E7E1',
        'radio://0/80/2M/E7E7E7E7E2',
        'radio://1/90/2M/E7E7E7E7E3',
        'radio://1/90/2M/E7E7E7E7E4',
        'radio://1/90/2M/E7E7E7E7E5',
        'radio://2/100/2M/E7E7E7E7E6',
        'radio://2/100/2M/E7E7E7E7E7',
        'radio://2/100/2M/E7E7E7E7E8'
]


def ohMy():
    print('uris meant to be touched on:')
    print(uris)
    for uri in uris:
        print('tipo:  ')
        print(uri)
        try:
            print('trying to power up %s' % uri) 
            # PowerSwitch(uri).stm_power_up()
        except Exception: 
            # print (Exception)
            print('%s is not there to be woken up, gonna pop it out from my list' % uri)
            connectedUris.remove(uri)
            time.sleep(1)

ohMy()
