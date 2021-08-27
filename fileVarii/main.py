#rf 2021
#ciao
import threading
import time
import signal
from   collections import namedtuple
from types import BuiltinFunctionType
#custom modules
import OSCStuff as OSC
import timerino as myTimer
import Drogno
import cflib.crtp

WE_ARE_FAKING_IT      = False



exit_event = threading.Event()

uris = [
        # 'radio://0/80/2M/E7E7E7E7E0',
        # 'radio://0/80/2M/E7E7E7E7E1',
        # 'radio://0/80/2M/E7E7E7E7E2',
        # possibili problemi hardware
        # 'radio://1/90/2M/E7E7E7E7E3',
        #  (vuoti d'aria?)
        # 'radio://1/90/2M/E7E7E7E7E4',
        # grande incertezza al centro - super compensazioni
        # 'radio://1/90/2M/E7E7E7E7E5',
        #  ok  
        # 'radio://2/100/2M/E7E7E7E7E6',
        #  il meglio
        # 'radio://2/100/2M/E7E7E7E7E7',
        # serii problemi radio
        # 'radio://2/100/2M/E7E7E7E7E8',
        #   gut
        'radio://3/110/2M/E7E7E7E7E9',
        # 'radio://0/110/2M/E7E7E7E7EA',
        ]
drogni = {}


    
def main():
    global WE_ARE_FAKING_IT
    if not WE_ARE_FAKING_IT:
        cflib.crtp.init_drivers(enable_debug_driver=False)

    try:
        availableRadios = cflib.crtp.scan_interfaces()
        if availableRadios:
            for i in availableRadios:
                print ('Found %s radios.' % len(availableRadios))
                print ("URI: [%s]   ---   name/comment [%s]" % (i[0], i[1]))
        else:
            WE_ARE_FAKING_IT = True
    except IndexError:
        print(IndexError)
 
    
    for uro in uris:
        iddio = int(uro[-1])
        drogni[int(iddio)] = Drogno.Drogno(iddio, uro, exit_event, WE_ARE_FAKING_IT)
        drogni[int(iddio)].start()
        # drogni[int(iddio)].join()
        # print(drogni)

    OSC.drogni = drogni
    OSC.faiIlBufferon()
    OSCRefreshThread      = threading.Thread(target=OSC.start_server,daemon=True).start()
    OSCPrintAndSendThread = threading.Thread(target=OSC.printAndSendCoordinates,daemon=True).start()


def exit_signal_handler(signum, frame):
    print('esco')
    exit_event.set() 
    OSC.finished = True
    drogni = {}

if __name__ == '__main__':
    # logging.basicConfig(level=logging.ERROR)
    main()
    signal.signal(signal.SIGINT, exit_signal_handler)

    while True:
        pass




