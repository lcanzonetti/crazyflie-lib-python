
import logging
import time
import OSCStuff
import win_ctrl_c
import threading
from threading import *
import logging

# logging.basicConfig(level=logging.DEBUG,format='(%(threadName)-9s) %(message)s',)

import cflib.crtp
from   cflib.crazyflie               import Crazyflie
from   cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from   cflib.utils                   import uri_helper
from   cflib.crazyflie.syncLogger    import SyncLogger
from   cflib.crazyflie.log           import LogConfig

# URI to the Crazyflie to connect to
# uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E8')
uris = [
        # 'radio://0/80/2M/E7E7E7E7E0',
        # 'radio://0/80/2M/E7E7E7E7E1',
        # 'radio://0/80/2M/E7E7E7E7E2',
        # 'radio://0/80/2M/E7E7E7E7E3',
        # 'radio://0/80/2M/E7E7E7E7E4',
        # 'radio://0/80/2M/E7E7E7E7E5',
        # 'radio://0/80/2M/E7E7E7E7E6',
        'radio://0/80/2M/E7E7E7E7E7',
        'radio://0/80/2M/E7E7E7E7E8'
        # 'radio://0/80/2M/E7E7E7E7E9',
        ]
drogni = []


# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

  
def crazyflie_connected():
    print('ho connesso un krezi flaio')
    # crazyflie.close_link()

def main():
    crazyflie = Crazyflie()
    crazyflie.connected.add_callback(crazyflie_connected)
    availableRadios = cflib.crtp.scan_interfaces()
    for i in availableRadios:
        print (i)
        print ("Interface with URI [%s] found and name/comment [%s]" % (i[0], i[1]))

    lg_stab = LogConfig(name='Stabilizer', period_in_ms=50)
    lg_stab.add_variable('stabilizer.roll', 'float')
    lg_stab.add_variable('stabilizer.pitch', 'float')
    lg_stab.add_variable('stabilizer.yaw', 'float')
    lg_stab.add_variable('lighthouse.x', 'float')
    lg_stab.add_variable('lighthouse.y', 'float')
    lg_stab.add_variable('lighthouse.z', 'float')
        
    for iddio in range (len(uris)):
        print('oddio!', iddio)
        drogni.append(Drogno(iddio, lg_stab))
        drogni[iddio].connect(uris[iddio])
    
    # while True:
    #     pass
        
class Drogno:
    def __init__(self, ID, logSettings):
        self.ID          = ID
        self.logSettings = logSettings
        print(f'ciao, sono un drogno, mi sono inizializzato con id {ID}')
    
    def sendNewHighLevelCommand():
        pass
    def connect(self, urio):
        with SyncCrazyflie(urio, cf=Crazyflie(rw_cache='./cache')) as scf:
             threading.Thread(target=self.loggalo,args=[scf, self.logSettings],daemon=True).start()
            # self.loggalo(scf, self.logSettings)

    def log_stab_callback(self, timestamp, data, logconf):
        # print('[%d][%s]: %s' % (timestamp, logconf, data))
        OSCStuff.sendRotation(self.ID, data['stabilizer.roll'], data['stabilizer.pitch'], data['stabilizer.yaw'] )
        OSCStuff.sendPose    (self.ID, data['lighthouse.x'], data['lighthouse.y'], data['lighthouse.z'] )

    def loggalo(self, scf, logconf):
        cf = scf.cf
        cf.log.add_config(logconf)
        logconf.data_received_cb.add_callback(self.log_stab_callback)
        logconf.start()
        print('loggo!', logconf)
        # while True:
        #     pass
        return

class RepeatedTimer:

    """Repeat `function` every `interval` seconds."""

    def __init__(self, interval, function, *args, **kwargs):
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.start = time.time()
        self.event = Event()
        self.thread = Thread(target=self._target)
        self.thread.start()

    def _target(self):
        while not self.event.wait(self._time):
            self.function(*self.args, **self.kwargs)

    @property
    def _time(self):
        return self.interval - ((time.time() - self.start) % self.interval)

    def stop(self):
        self.event.set()
        self.thread.join()


if __name__ == '__main__':

    # cflib.crtp.init_drivers()
    cflib.crtp.init_drivers(enable_debug_driver=False)
    # start timer
    # timer = RepeatedTimer(0.01, OSCSend.osc_process)
    # def cazzone():
    #     msg = OSCSend.oscbuildparse.OSCMessage("/test/me", ",sif", ["text", 672, 8.871])
    #     OSCSend.osc_send(msg, "drognoBack")
    # timer2 = RepeatedTimer(1, cazzone)
    main()

