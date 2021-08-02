
import logging
import time
import win_ctrl_c
import threading
from threading import *
import logging
import concurrent.futures
import cflib.crtp
from   cflib.crazyflie                            import Crazyflie
from   cflib.crazyflie.syncCrazyflie              import SyncCrazyflie
from   cflib.utils                                import uri_helper
from   cflib.crazyflie.syncLogger                 import SyncLogger
from   cflib.crazyflie.log                        import LogConfig
from   cflib.positioning.position_hl_commander import PositionHlCommander
from   console.utils import wait_key
import OSCStuff

uris = [
        # 'radio://0/80/2M/E7E7E7E7E0',
        # 'radio://0/80/2M/E7E7E7E7E1',
        # 'radio://0/80/2M/E7E7E7E7E2',
        # 'radio://0/80/2M/E7E7E7E7E3',
        # 'radio://0/80/2M/E7E7E7E7E4',
        # 'radio://0/80/2M/E7E7E7E7E5',
        # 'radio://0/80/2M/E7E7E7E7E6',
        'radio://0/80/2M/E7E7E7E7E7',
        'radio://0/80/2M/E7E7E7E7E8',
        # 'radio://0/80/2M/E7E7E7E7E9',
        ]
drogni = {}
# DEFAULT_HEIGHT = 0.5
# BOX_LIMIT = 0.5
# position_estimate = [0, 0]
logging.basicConfig(level=logging.ERROR)


def main():
    availableRadios = cflib.crtp.scan_interfaces()
    for i in availableRadios:
        print (i)
        print ("Interface with URI [%s] found and name/comment [%s]" % (i[0], i[1]))
 

        
    for uro in uris:
        iddio = int(uro[-1])
        drogni[int(iddio)] = Drogno(iddio, uro)

    
    OSCStuff.svormo = drogni
    print('drogni:')
    print(drogni)

    for drogno in drogni:
        drogni[drogno].connect()
        
class Drogno():
    def __init__(self, ID, link_uri):
        self.ID  = ID
        self.commander = None
        self.link_uri = link_uri
        self.recconnectionAttempts = 0
        self._cf = Crazyflie(rw_cache='./cache')
        # Connect some callbacks from the Crazyflie API
        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)
        # Try to connect to the Crazyflie
        self.is_connected = False
        # self.logSettings = logSettings
    def connect(self):
        print(f'Provo a connettermi al drone { self.ID} all\'indirizzo { self.link_uri} ')
        if self.recconnectionAttempts < 10:
            print('Aspetto 1 secondo')
            time.sleep(0.1)
            print(f'provo a riaprire la connessione con il drogno {self.ID} dopo {self.recconnectionAttempts} tentativi.')
            self.recconnectionAttempts+=1
            self._cf.open_link( self.link_uri)

        else:
            print('con il drogno %s ho perso le speranze' % self.ID)

    def _connected(self, link_uri):
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""
        print('Connected to %s' % link_uri)
        # Variable used to keep main loop occupied until disconnect
        self.is_connected = True
        # The definition of the logconfig can be made before connecting
        self._lg_stab = LogConfig(name='Stabilizer', period_in_ms=50)
        self._lg_stab.add_variable('stateEstimate.x', 'float')
        self._lg_stab.add_variable('stateEstimate.y', 'float')
        self._lg_stab.add_variable('stateEstimate.z', 'float')
        self._lg_stab.add_variable('stabilizer.roll', 'float')
        self._lg_stab.add_variable('stabilizer.pitch', 'float')
        self._lg_stab.add_variable('stabilizer.yaw', 'float')
        # self._lg_stab = LogConfig(name='Lighthouse', period_in_ms=50)
        # self._lg_stab.add_variable('lighthouse.x', 'float')
        # self._lg_stab.add_variable('lighthouse.y', 'float')
        # self._lg_stab.add_variable('lighthouse.z', 'float')
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
            with PositionHlCommander(
            self._cf,
            # x=0.0, y=0.0, z=0.0,
            # default_velocity=0.3,
            # default_height=0.5,
            controller=PositionHlCommander.CONTROLLER_PID) as pc:
                self.commander = pc
                # self.sequenzaTest()

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
        print(f'[{timestamp}][{logconf.name}]: ', end='')
        for name, value in data.items():
            print(f'{name}: {value:3.3f} ', end='')
        # print()
        OSCStuff.sendRotation(self.ID, data['stabilizer.roll'], data['stabilizer.pitch'], data['stabilizer.yaw'] )
        OSCStuff.sendPose    (self.ID, data['stateEstimate.x'], data['stateEstimate.y'], data['stateEstimate.z'] )
        # OSCStuff.sendPose    (self.ID, data['lighthouse.x'], data['lighthouse.y'], data['lighthouse.z'] )
        # OSCStuff.sendPose    (self.ID, -2.5+self.ID, 0.02, -2.01 )

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the specified address)"""
        print('Connessione la drogno %s fallita: %s' % (self.ID, msg))
        self.is_connected = False
        self.connect()

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print('Me son perso %s dice: %s' % (link_uri, msg))
        self.is_connected = False
        time.sleep(0.5)
        self.connect()

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected (called in all cases)"""
        print('Deh, son sconnesso da %s' % link_uri)
        self.is_connected = False
        time.sleep(0.5)
        self.connect()

    def goTo(self,x,y,z):
        self.commander.go_to(x,y,z)
    def sequenzaTest(self):
        # self.commander.go_to(0.0, 0.5, 0.0)
        self.commander.go_to(0.0, 0.3, 0.1)
        self.commander.go_to(0.0, 0.3, 0.0)
        # self.commander.up(1.0)




if __name__ == '__main__':

    cflib.crtp.init_drivers(enable_debug_driver=False)
   
    # def cazzone():
    #     msg = OSCSend.oscbuildparse.OSCMessage("/test/me", ",sif", ["text", 672, 8.871])
    #     OSCSend.osc_send(msg, "drognoBack")
    # timer2 = RepeatedTimer(1, cazzone)
    main()

