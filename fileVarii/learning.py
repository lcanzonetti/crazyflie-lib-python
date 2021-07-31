
import logging
import time
import OSCStuff
import win_ctrl_c
import threading
from threading import *
import logging
import concurrent.futures

import cflib.crtp
from   cflib.crazyflie               import Crazyflie
from   cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from   cflib.utils                   import uri_helper
from   cflib.crazyflie.syncLogger    import SyncLogger
from   cflib.crazyflie.log           import LogConfig

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

logging.basicConfig(level=logging.ERROR)

def main():
   
    availableRadios = cflib.crtp.scan_interfaces()
    for i in availableRadios:
        print (i)
        print ("Interface with URI [%s] found and name/comment [%s]" % (i[0], i[1]))

    # lg_stab.add_variable('lighthouse.x', 'float')
    # lg_stab.add_variable('lighthouse.y', 'float')
    # lg_stab.add_variable('lighthouse.z', 'float')
        
    for uro in uris:
        iddio = int(uro[-1])
        print('oddio!', iddio)
        drogni.append(Drogno(iddio, uro))
    
    for drogno in drogni:
        if drogno.is_connected:
            # time.sleep(1)
            pass
        else:
            print('na? se so sconnessi tutti')
        
class Drogno():
    def __init__(self, ID, link_uri):
        self.ID  = ID
        self._cf = Crazyflie(rw_cache='./cache')
        # Connect some callbacks from the Crazyflie API
        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)

        # Try to connect to the Crazyflie
        self._cf.open_link(link_uri)
        print('Mi connetto a %s' % link_uri)

        # Variable used to keep main loop occupied until disconnect
        self.is_connected = True

        # self.logSettings = logSettings
        print(f'ciao, sono una classe drogno, mi sono inizializzato con id {ID}')

    def _connected(self, link_uri):
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""
        print('Connected to %s' % link_uri)

        # The definition of the logconfig can be made before connecting
        self._lg_stab = LogConfig(name='Stabilizer', period_in_ms=50)
        self._lg_stab.add_variable('stateEstimate.x', 'float')
        self._lg_stab.add_variable('stateEstimate.y', 'float')
        self._lg_stab.add_variable('stateEstimate.z', 'float')
        self._lg_stab.add_variable('stabilizer.roll', 'float')
        self._lg_stab.add_variable('stabilizer.pitch', 'float')
        self._lg_stab.add_variable('stabilizer.yaw', 'float')
        # The fetch-as argument can be set to FP16 to save space in the log packet
        self._lg_stab.add_variable('pm.vbat', 'FP16')

        # Adding the configuration cannot be done until a Crazyflie is
        # connected, since we need to check that the variables we
        # would like to log are in the TOC.
        try:
            self._cf.log.add_config(self._lg_stab)
            # This callback will receive the data
            self._lg_stab.data_received_cb.add_callback(self._stab_log_data)
            # This callback will be called on errors
            self._lg_stab.error_cb.add_callback(self._stab_log_error)
            # Start the logging
            self._lg_stab.start()
        except KeyError as e:
            print('Could not start log configuration,'
                  '{} not found in TOC'.format(str(e)))
        except AttributeError:
            print('Could not add Stabilizer log config, bad configuration.')

        # Start a timer to disconnect in 10s
        # t = Timer(5, self._cf.close_link)
        # t.start()

    def _stab_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print('Error when logging %s: %s' % (logconf.name, msg))

    def _stab_log_data(self, timestamp, data, logconf):
        # """Callback from a the log API when data arrives"""
        # print(f'[{timestamp}][{logconf.name}]: ', end='')
        # for name, value in data.items():
        #     print(f'{name}: {value:3.3f} ', end='')
        # print()
        OSCStuff.sendRotation(self.ID, data['stabilizer.roll'], data['stabilizer.pitch'], data['stabilizer.yaw'] )
        # OSCStuff.sendPose    (self.ID, data['stateEstimate.x'], data['stateEstimate.y'], data['stateEstimate.z'] )
        OSCStuff.sendPose    (self.ID, -2.5+self.ID, 0.02, -2.01 )

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the specified address)"""
        print('Connection to %s failed: %s' % (link_uri, msg))
        self.is_connected = False
        time.sleep(0.5)
        self._cf.open_link(link_uri)


    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print('Me son perso %s dice: %s' % (link_uri, msg))

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected (called in all cases)"""
        print('Deh, son sconnesso da %s' % link_uri)
        self.is_connected = False
        time.sleep(0.5)
        self._cf.open_link(link_uri)

    def sendNewHighLevelCommand():
        pass

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

