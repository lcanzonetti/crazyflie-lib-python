import threading
import time
import random
import concurrent.futures
from   collections import namedtuple
#custom modules
import OSCStuff as OSC
import timerino as myTimer
#crazyflie's
import logging
import cflib.crtp
from   cflib.crazyflie                            import Crazyflie, commander
from   cflib.crazyflie.syncCrazyflie              import SyncCrazyflie
from   cflib.utils                                import uri_helper
from   cflib.crazyflie.syncLogger                 import SyncLogger
from   cflib.crazyflie.log                        import LogConfig
from   cflib.positioning.position_hl_commander import PositionHlCommander


we_are_faking_it = False


uris = [
        # 'radio://0/80/2M/E7E7E7E7E0',
        # 'radio://0/80/2M/E7E7E7E7E1',
        # 'radio://0/80/2M/E7E7E7E7E2',
        # 'radio://0/80/2M/E7E7E7E7E3',
        'radio://0/80/2M/E7E7E7E7E4',
        # 'radio://0/80/2M/E7E7E7E7E5',
        # 'radio://0/80/2M/E7E7E7E7E6',
        'radio://0/80/2M/E7E7E7E7E7',
        # 'radio://0/80/2M/E7E7E7E7E8',
        # 'radio://0/80/2M/E7E7E7E7E9',
        ]
drogni = {}
DEFAULT_HEIGHT   = 0.5
BOX_LIMIT        = 1.2
RELATIVE_SPACING = 0.4


# Possible commands, all times are in seconds
Takeoff = namedtuple('Takeoff', ['height', 'time'])
Land = namedtuple("Land", ['time'])
Goto = namedtuple('Goto', ['x', 'y', 'z', 'time'])
Ring = namedtuple('Ring', ['r', 'g', 'b', 'intensity', 'time'])   # RGB [0-255], Intensity [0.0-1.0]
Quit = namedtuple('Quit', []) # Reserved for the control loop, do not use in sequence



def main():
    availableRadios = cflib.crtp.scan_interfaces()
    for i in availableRadios:
        print (i)
        print ("Interface with URI [%s] found and name/comment [%s]" % (i[0], i[1]))
 
    for uro in uris:
        iddio = int(uro[-1])
        drogni[int(iddio)] = Drogno(iddio, uro)
        drogni[int(iddio)].start()

    OSC.drogni = drogni
        
class Drogno(threading.Thread):
    def __init__(self, ID, link_uri):
        threading.Thread.__init__(self)
        self.link_uri    = link_uri
        self.ID          = int(ID)
        self.name        = 'Drogno_'+str(ID)
        self.statoDiVolo = 'starting'
        self.durataVolo  = random.randint(1,4)
        self.exitFlag    = 0
        self.isReadyToFly          = False
        self.isFlyng               = False
        self.controlThread         = False
        self.printThread           = False
        self.printRate             = 1     #seconds
        self.currentSequenceThread = False
        self.exitingTimer          = False
        self.idleExitTime          = 10    #seconds
        self.recconnectionAttempts = 0
        self.is_connected          = False
        self.isPositionEstimated   = True
        self.commander   = None
        self._cf = Crazyflie(rw_cache='./cache'+str(ID))
        # Connect some callbacks from the Crazyflie API
        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)
     
    def run(self):
        print ("Starting " + self.name)

        if we_are_faking_it:
            time.sleep(1.5)
        else:
            self.connect()
    
        self.statoDiVolo   = 'idle'
        self.controlThread = threading.Thread(target=self.controlThreadRoutine).start()
        self.printThread   = threading.Thread(target=self.printStatus).start()
        while not self.exitFlag:
            pass
        print ("Exiting "  + self.name)

    def exit(self):
                print('exitFlag is now set for drogno %s, bye kiddo' % self.name)       
                self.exitFlag = 1

    def printStatus(self):
        while not self.exitFlag:
            time.sleep(self.printRate)
            print ("%s: %s" % (self.name, self.statoDiVolo))
            # print ("%s: %s : %s" % (threadName, time.ctime(time.time()), self.statoDiVolo))
    
    def controlThreadRoutine(self):
        print('control routine for %s started' % self.name)
        while not self.exitFlag:
            if  (self.statoDiVolo == 'sequenza simulata!'):
                self.sequenzaDiVoloSimulata()
                if self.exitingTimer != False:
                    self.exitingTimer.stop()
                    self.exitFlag = 0
            elif (self.statoDiVolo == 'landing'):
                if we_are_faking_it:
                    time.sleep(2)
                    self.statoDiVolo = 'idle'
                else:
                    self.statoDiVolo = 'yo lando'
              
                # self.exitingTimer = myTimer.Timer(self.idleExitTime, self.exit).start()
                # print (self.exitingTimer)
                # print('exiting in 5 seconds') 

    def sequenzaDiVoloSimulata(self):     
        def volo():
            print('il drone %s vola! e volerà per %s secondi' % (self.ID, self.durataVolo))
            time.sleep(self.durataVolo)
            self.statoDiVolo = 'finito sequenza'
            # self.currentSequenceThread.join()

        if not self.currentSequenceThread:
            self.currentSequenceThread = threading.Thread(target=volo)
            self.currentSequenceThread.start()
            print('start!')
        # else:
            # print ('il thread di volo è già iniziato_______')

    def connect(self):
        print(f'Provo a connettermi al drone { self.ID} all\'indirizzo { self.link_uri} ')
        self._cf.open_link( self.link_uri)

    def reconnect(self):
        if self.recconnectionAttempts == 0:
            print(f'provo a riaprire la connessione con il drogno {self.name}')
            self.recconnectionAttempts+=1
            self._cf.open_link( self.link_uri)

        elif self.recconnectionAttempts >= 1 and self.recconnectionAttempts < 10:
            while self.is_connected == False and self.recconnectionAttempts < 10: 
                print(f'provo a riaprire la connessione con il drogno {self.name} dopo {self.recconnectionAttempts} tentativi.')
                self.recconnectionAttempts +=1
                self._cf.open_link( self.link_uri)
                print('Aspetto 1 secondo')
                time.sleep(1)
        else:
            print('con il drogno %s ho perso le speranze' % self.ID)
            self.exit()

    def activate_mellinger_controller(self, use_mellinger):
        controller = 1
        if use_mellinger:
            controller = 2
        self._cf.cf.param.set_value('stabilizer.controller', controller)

    def wait_for_position_estimator(self):
        print('Waiting for estimator to find position...')

        log_config = LogConfig(name='Kalman Variance', period_in_ms=500)
        log_config.add_variable('kalman.varPX', 'float')
        log_config.add_variable('kalman.varPY', 'float')
        log_config.add_variable('kalman.varPZ', 'float')

        var_y_history = [1000] * 10
        var_x_history = [1000] * 10
        var_z_history = [1000] * 10

        threshold =5
        # threshold = 0.01

        with SyncLogger(self._cf, log_config) as logger:
            print('estimation logger started')
            for log_entry in logger:
                print(log_entry)
                data = log_entry[1]

                var_x_history.append(data['kalman.varPX'])
                var_x_history.pop(0)
                var_y_history.append(data['kalman.varPY'])
                var_y_history.pop(0)
                var_z_history.append(data['kalman.varPZ'])
                var_z_history.pop(0)

                min_x = min(var_x_history)
                max_x = max(var_x_history)
                min_y = min(var_y_history)
                max_y = max(var_y_history)
                min_z = min(var_z_history)
                max_z = max(var_z_history)

                print("{} {} {}".format(max_x - min_x, max_y - min_y, max_z - min_z))
                if (max_x - min_x) < threshold and (
                    max_y - min_y) < threshold and (
                    max_z - min_z) < threshold:
                    break
        print('positionEstimated')
        self.isPositionEstimated = True

    def reset_estimator(self):
        self._cf.param.set_value('kalman.resetEstimation', '1')
        time.sleep(0.1)
        self._cf.param.set_value('kalman.resetEstimation', '0')
        self.wait_for_position_estimator()

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
            time.sleep(0.3)
            # self.reset_estimator()

            self._lg_stab.start()
            self._cf.param.set_value('commander.enHighLevel', '1')
            self.setRingColor(0,0,0, 0, 0)
            self._cf.param.set_value('ring.effect', '14')
            self.commander = self._cf.high_level_commander
            self.isReadyToFly = True
     
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

    def _stab_log_data(self, timestamp, data, logconf):  #riceve il feedback dei sensori e smista i dati
        # """Callback from a the log API when data arrives"""
        print(f'[{timestamp}][{logconf.name}]: ', end='')
        for name, value in data.items():
            print(f'{name}: {value:3.3f} ', end='')
        # print()
        OSC.sendRotation(self.ID, data['stabilizer.roll'], data['stabilizer.pitch'], data['stabilizer.yaw'] )
        OSC.sendPose    (self.ID, data['stateEstimate.x'], data['stateEstimate.y'], data['stateEstimate.z'] )
        self.evaluateBattery(data['pm.vbat'])
        # OSCStuff.sendPose    (self.ID, data['lighthouse.x'], data['lighthouse.y'], data['lighthouse.z'] )
        # OSCStuff.sendPose    (self.ID, -2.5+self.ID, 0.02, -2.01 )

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the specified address)"""
        print('Connessione la drogno %s fallita: %s' % (self.ID, msg))
        self.is_connected = False
        self.statoDiVolo = 'sconnesso'
        self._cf.close_link()
        time.sleep(1)
        self.reconnect()

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print('Me son perso %s dice: %s' % (link_uri, msg))
        self.is_connected = False
        self.statoDiVolo = 'sconnesso'
        self._cf.close_link()
        time.sleep(1)
        self.reconnect()

    def _disconnected(self, link_uri):
        if self.is_connected == True:
            """Callback when the Crazyflie is disconnected (called in all cases)"""
            print('Deh, son sconnesso da %s' % link_uri)
            self.is_connected = False
            self.statoDiVolo = 'sconnesso'
            self._cf.close_link()
            time.sleep(1)
            self.reconnect()

    def takeoff(self, height=DEFAULT_HEIGHT, time=1.5):
        print('like, now')
        if we_are_faking_it:
            time.delay(1)
            self.statoDiVolo = 'decollato!'
            self.isFlyng     = True
        else:
            print('for real')
            if self.isReadyToFly:
                self.commander.takeoff(0.45, 2.45)
                self.statoDiVolo = 'decollato!'
                self.isFlyng     = True
            else:
                print('BUT NOT READY')


    def go(self, sequenceNumber=0):
        if self.statoDiVolo == 'decollato!' or self.statoDiVolo == 'finito sequenza':
            if we_are_faking_it:
                self.statoDiVolo = 'sequenza simulata!'
            else:
                self.sequenzaTest(sequenceNumber)
        else:
            print('not ready!')

    def land(self):
        if self.isFlyng:
            if we_are_faking_it:
                time.sleep(1)
                self.statoDiVolo = 'landing'
            else:
                self.commander.land()
            self.isFlyng     = False
            self.isReadyToFly = True
        else:
            print('not flying anymore')
       

    def goTo(self,x,y,z):  #la zeta è in alto!
        self.commander.go_to(x,y,z)
    
    def setRingColor(self, r, g, b, intensity = 1.0, time=1.0):
        self._cf.param.set_value('ring.fadeTime', str(time))
        r *= intensity
        g *= intensity
        b *= intensity
        color = (int(r) << 16) | (int(g) << 8) | int(b)
        self._cf.param.set_value('ring.fadeColor', str(color))

    def sequenzaTest(self,sequenceNumber):
        if  sequenceNumber == 0:
            print('Drogno: %s. Inizio ciclo decollo/atterraggio di test' % self.ID)
            input("enter to continue")
            self.commander.go_to(0.0, 0.0, 0.5)
            self.commander.go_to(0.0, 0.0, 1.0)
            self.commander.go_to(0.0, 0.0, 0.5)
            print('Drogno: %s. Fine ciclo decollo/atterraggio di test' % self.ID)
        elif sequenceNumber == 1:
            print('inizio prima sequenza di test')
            self.commander.go_to(0.0, 0.0, 1)
            self.setRingColor(255,   0,   0, 1.0, 1.0)
            time.sleep(1)

            self.commander.go_to(0.0, 1+RELATIVE_SPACING, 1)
            self.setRingColor(255,   0,   0, 1.0, 1.0)

            self.commander.go_to(1+RELATIVE_SPACING, 1+RELATIVE_SPACING, 1)
            self.setRingColor(  0, 255,  0, 1.0, 1.0)
            
            self.commander.go_to(1.0+RELATIVE_SPACING, 0.0+RELATIVE_SPACING, 1)
            self.setRingColor(  0,   0, 255, 1.0, 1.0)

            self.commander.go_to(0.0+RELATIVE_SPACING, 0.0+RELATIVE_SPACING, 1)
            self.setRingColor(255, 255,   0, 1.0, 1.0)
            time.sleep(1)

            self.setRingColor(255, 255,   0, 1.0, 1.0)
            time.sleep(1)
            self.setRingColor(255, 255,   0, 1.0, 1.0)
            time.sleep(1)
            print('fine prima sequenza di test')

    def evaluateBattery(self, level):
        if level<3.54:
            print ('ciao, sono il drone %s e ho la batteria scarica' % self.ID)
        if level<3.45:
            print ('ciao, sono il drone %s e sono così scarico che atterrerei.' % self.ID)
        


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    main()

