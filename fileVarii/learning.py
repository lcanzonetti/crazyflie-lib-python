
import logging
import time
import threading
import OSCSend

import cflib.crtp
from   cflib.crazyflie               import Crazyflie
from   cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from   cflib.utils                   import uri_helper
from   cflib.crazyflie.syncLogger    import SyncLogger
from   cflib.crazyflie.log           import LogConfig

# URI to the Crazyflie to connect to
# uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E8')
uri = 'radio://0/80/2M/E7E7E7E7E7'
# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

def log_stab_callback(timestamp, data, logconf):
    # print('[%d][%s]: %s' % (timestamp, logconf, data))
    OSCSend.sendRotation(1, data['stabilizer.roll'], data['stabilizer.pitch'], data['stabilizer.yaw'] )
    # print(data)

def loggalo(scf, logconf):
    cf = scf.cf
    cf.log.add_config(logconf)
    logconf.data_received_cb.add_callback(log_stab_callback)
    logconf.start()
    print('loggo!', logconf)
    while True:
        pass
    # time.sleep(5)
    # logconf.stop()

def crazyflie_connected():
    print('ho connesso un krezi flaio')
    # crazyflie.close_link()

def main():
    
    crazyflie = Crazyflie()
    crazyflie.connected.add_callback(crazyflie_connected)

    available = cflib.crtp.scan_interfaces()
    for i in available:
        print (i)
        print ("Interface with URI [%s] found and name/comment [%s]" % (i[0], i[1]))

    lg_stab = LogConfig(name='Stabilizer', period_in_ms=50)
    lg_stab.add_variable('stabilizer.roll', 'float')
    lg_stab.add_variable('stabilizer.pitch', 'float')
    lg_stab.add_variable('stabilizer.yaw', 'float')

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:

        # treddoDelLog = threading.Thread(target=loggalo, args=[scf, lg_stab])
        # treddoDelLog.daemon = True
        # treddoDelLog.start()
        loggalo(scf, lg_stab)

    while True:
        pass
        

# # Properly close the system.
# OSCSend.osc_terminate()



from threading import Event, Thread

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
    timer = RepeatedTimer(0.05, OSCSend.osc_process)
    # def cazzone():
    #     msg = OSCSend.oscbuildparse.OSCMessage("/test/me", ",sif", ["text", 672, 8.871])
    #     OSCSend.osc_send(msg, "drognoBack")
    # timer2 = RepeatedTimer(1, cazzone)
    main()

