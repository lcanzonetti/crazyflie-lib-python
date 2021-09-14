#rf 2021
import threading
import multiprocessing
from multiprocessing.connection import Client
import OSC_feedabcker as feedbacker

import time
import random
from   colorama             import Fore, Back, Style
from   colorama             import init as coloInit

          
coloInit(convert=True)

#crazyflie's
import logging
from   cflib.crazyflie                            import Crazyflie, commander
from   cflib.crazyflie.syncCrazyflie              import SyncCrazyflie
from   cflib.utils                                import uri_helper
from   cflib.crazyflie.syncLogger                 import SyncLogger
from   cflib.crazyflie.log                        import LogConfig
from   cflib.positioning.position_hl_commander    import PositionHlCommander
from   cflib.crazyflie.mem import MemoryElement
from   cflib.crazyflie.mem import Poly4D
from   cflib.utils.power_switch import PowerSwitch
logging.basicConfig(level=logging.ERROR)

BOX_X                 = 1.5
BOX_Y                 = 1.5
BOX_Z                 = 1.9
DEFAULT_HEIGHT        = 0.9
RELATIVE_SPACING      = 0.4
BATTERY_CHECK_RATE    = 1.0
STATUS_PRINT_RATE     = 2.0
COMMANDS_FREQUENCY    = 0.2
LOGGING_FREQUENCY     = 400
FEEDBACK_SENDING_PORT = 6000
FEEDBACK_ENABLED      = True
RING_FADE_TIME        = 0.8


class Drogno(threading.Thread):
    def __init__(self, ID, link_uri, exitFlag, processes_exit_event, perhapsWeReFakingIt, startingPoint, lastRecordPath):
        threading.Thread.__init__(self)
        self.lastRecordPath  = lastRecordPath
        self.lastTrajectory  = ''
        self.TRAJECTORIES    = {}
        self.currentTrajectoryLenght = 0
        self.link_uri    = link_uri
        self.ID          = int(ID)
        self.name        = 'Drogno_'+str(ID)
        self.statoDiVolo = 'starting'
        self.durataVolo  = random.randint(1,4)
        self.exitFlag    = exitFlag
        self.WE_ARE_FAKING_IT = perhapsWeReFakingIt
        self.isKilled              = False
        self.isReadyToFly          = False
        self.isFlying              = False
        self.controlThread         = False
        self.printThread           = False
        self.printRate             = STATUS_PRINT_RATE
        self.currentSequenceThread = False
        self.recconnectionAttempts = 0
        self.is_connected          = False
        self.standBy               = False
        self.isPositionEstimated   = False
        self.HLCommander           = None
        self.positionHLCommander   = None 
        self.starting_x            = 'np'
        self.starting_y            = 'np'
        self.starting_z            = 'np'
        self.x                     = 0.0
        self.y                     = 0.0 
        self.z                     = 0.0
        self.requested_X           = 0.0
        self.requested_Y           = 0.0
        self.requested_Z           = 0.0
        self.requested_R           = 0
        self.requested_G           = 0
        self.requested_B           = 0
        self.kalman_VarX              = 0
        self.kalman_VarY              = 0
        self.kalman_VarZ              = 0
        self.esteemsCount           = 0
        self.prefStartPoint_X      = startingPoint[0]
        self.prefStartPoint_Y      = startingPoint[1]
        self.yaw                   = 0.0
        self.batteryVoltage        = 'n.p.'
        self.ringIntensity         = 0.1
        self.goToCount             = 0.0
        self.multiprocessConnection = None
        self._cf = Crazyflie(rw_cache='./cache')
        # Connect some callbacks from the Crazyflie API
        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)
        self.feedbacker_port      = 9100 + self.ID
        self.feedbacker_address   = ('127.0.0.1', self.feedbacker_port)
        self.feedbacker           = feedbacker.Feedbacco(processes_exit_event,  self.feedbacker_port  )
        self.OSCFeedbackProcess   = multiprocessing.Process(target=self.feedbacker.start).start()

    def run(self):
        print (Fore.LIGHTBLUE_EX + "Starting " + self.name)
        self.TRAJECTORIES [0] = self.lastRecordPath + '/trajectory_' + str(self.ID) + '.txt'
        self.TRAJECTORIES [7] = figure8Triple
        self.TRAJECTORIES [8] = figure8
    
        # print ('my trajectories are: %s' % self.TRAJECTORIES [8])
        # with open(trajectory, 'r') as t:
        #     # print(t.readlines())
        #     self.lastTrajectory = t.readlines()

        if self.WE_ARE_FAKING_IT:
            print (Fore.LIGHTBLUE_EX + "Faking it = " + str(self.WE_ARE_FAKING_IT ))
            time.sleep(1.5)
            # print('fKING IT')
            # self.multiprocessConnection.send([self.ID, self.x, self.y, self.z, 4.2])
        else:
            print('We are not faking it this time.')
            connectedToFeedback = False
            if FEEDBACK_ENABLED and  not self.exitFlag.is_set():
                while not connectedToFeedback:
                    try:
                        time.sleep(1)
                        self.multiprocessConnection = Client(self.feedbacker_address)
                        connectedToFeedback = True
                    except ConnectionRefusedError:
                        print('server di feedback non connesso!')

            self.printThread   = threading.Thread(target=self.printStatus).start()
            self.batteryThread = threading.Thread(target=self.evaluateBattery)
            self.connect()
     
    def printStatus(self):
        while not self.exitFlag.is_set():
            time.sleep(self.printRate)
            if self.is_connected:
                print (Fore.GREEN  +  f"{self.name}: {self.statoDiVolo}\tbattery {self.batteryVoltage}\tpos {self.x:0.2f} {self.y:0.2f} {self.z:0.2f}\tyaw: {self.yaw:0.2f}\tmsg/s {self.goToCount/self.printRate}\tkalman var: {round(self.kalman_VarX,3)} {round(self.kalman_VarY,3)} {round(self.kalman_VarZ,3)}")
                self.goToCount = 0
                # print ('kalman var: %s %s %s' % (round(self.kalman_VarX,3), round(self.kalman_VarY,3), round(self.kalman_VarZ,3)))
            else:
                print (Fore.LIGHTBLUE_EX  +  f"{self.name}: {self.statoDiVolo}  msg/s {self.goToCount/self.printRate}")
        print('Sono stato %s ma ora non sono più' % self.name)
                    
    def sequenzaDiVoloSimulata(self):     
        def volo():
            print('il drone %s vola! e volerà per %s secondi' % (self.ID, self.durataVolo))
            time.sleep(self.durataVolo)
            self.statoDiVolo = 'hovering'

        if not self.currentSequenceThread:
            self.currentSequenceThread = threading.Thread(target=volo)
            self.currentSequenceThread.start()
            print('start!')

    def connect(self): 
        print(f'Provo a connettermi al drone { self.ID} all\'indirizzo { self.link_uri}    ')

        def porcoMondo():
            self.statoDiVolo = 'connecting'
            try:
                self._cf.open_link(self.link_uri)
            except IndexError:
                print('capperi')
            except:
                print('no radio pal')
        if self.killed == False:
            connessione = threading.Thread(target=porcoMondo, daemon=True).start() 

    def reconnect(self):
        # self._cf.close_link()
        def mariconnetto():
            if self.recconnectionAttempts == 0:
                print(f'provo a riaprire la connessione con il drogno {self.name}')
                self.recconnectionAttempts+=1
                self._cf.open_link( self.link_uri)

            elif self.recconnectionAttempts >= 1 and self.recconnectionAttempts < 10:
                while self.is_connected == False and self.recconnectionAttempts < 10: 
                    self.recconnectionAttempts +=1
                    print('Aspetto 1 secondo prima di ritentare')
                    time.sleep(1)
                    print(f'provo a riaprire la connessione con il drogno {self.name} dopo {self.recconnectionAttempts} tentativi.')
                    self.connect()
            else:
                print('con il drogno %s ho perso le speranze' % self.ID)
                self.exit()
        tio = 'something'
        tio = threading.Thread(target=mariconnetto)
        tio.start()
        
    def activate_mellinger_controller(self, use_mellinger):
        controller = 1
        if use_mellinger:
            controller = 2
        self._cf.cf.param.set_value('stabilizer.controller', controller)

    def wait_for_position_estimator(self):   # la proviamo 'sta cosa?
        self.isReadyToFly = False
        self.isPositionEstimated = False
        global esteemCount
        def orco():
            print('Waiting for estimator to find position...')
            currentEsteem_x = 0
            currentEsteem_y = 0
            currentEsteem_z = 0
            var_y_history = [] 
            var_x_history = [] 
            var_z_history = [] 
            var_x_history.append(currentEsteem_x)
            var_y_history.append(currentEsteem_y)
            var_z_history.append(currentEsteem_z)
            self.esteemsCount =  0
            def addKalmanDatas():
                # var_y_history = [1000] * 10
                # var_x_history = [1000] * 10
                # var_z_history = [1000] * 10
                # threshold =5
                threshold = 0.01
                if self.kalman_VarX != currentEsteem_x:
                    var_x_history.append(self.kalman_VarX)
                    var_x_history.pop(0)
                    self.esteemsCount += 1
                if self.kalman_VarY != currentEsteem_x:
                    var_y_history.append(self.kalman_VarY)
                    var_y_history.pop(0) 
                    self.esteemsCount += 1

                if self.kalman_VarZ != currentEsteem_x:
                    var_z_history.append(self.kalman_VarZ)
                    var_z_history.pop(0) 
                    self.esteemsCount += 1

                if self.esteemsCount > 30:
                        
                    min_x = min(var_x_history)
                    max_x = max(var_x_history)
                    min_y = min(var_y_history)
                    max_y = max(var_y_history)
                    min_z = min(var_z_history)
                    max_z = max(var_z_history)

                    # print("{} {} {}".format(max_x - min_x, max_y - min_y, max_z - min_z))
                    if (max_x - min_x) < threshold and (
                        max_y - min_y) < threshold and (
                        max_z - min_z) < threshold:
                        self.isPositionEstimated = True
                    if self.kalman_VarX < threshold and self.kalman_VarY < threshold and self.kalman_VarZ < threshold:
                        self.isPositionEstimated = True
                # self.isPositionEstimated = False
                print('position not yet estimated, got %s esteems' % self.esteemsCount)
            while not self.isPositionEstimated:
                addKalmanDatas()
            print('positionEstimated')
            self.isReadyToFly = self.evaluateFlyness()
        lanciaOrco = threading.Thread(target=orco).start()

    def reset_estimator(self):
        self._cf.param.set_value('kalman.resetEstimation', '1')
        time.sleep(0.2)
        self._cf.param.set_value('kalman.resetEstimation', '0')
        time.sleep(0.2)
        # self.wait_for_position_estimator()
        self.isReadyToFly = self.evaluateFlyness()
        self.isPositionEstimated = True
    #################################################################### connection

    def connect(self):
        if self.isKilled == False:
            print(f'Provo a connettermi al drone { self.ID} all\'indirizzo { self.link_uri}    ')
            def connection():
                self.statoDiVolo = 'connecting'
                try:
                    self._cf.open_link(self.link_uri)
                except IndexError:
                    print('capperi')
                except:
                    print('no radio pal')
            connessione = threading.Thread(target=connection).start() 

    def reconnect(self):
        def mariconnetto():
            if self.recconnectionAttempts == 0:
                print(f'provo a riaprire la connessione con il drogno {self.name}')
                self.recconnectionAttempts+=1
                self.connect()
            elif self.recconnectionAttempts >= 1 and self.recconnectionAttempts < 10:
                while self.is_connected == False and self.recconnectionAttempts < 10: 
                    self.recconnectionAttempts +=1
                    print('Aspetto 1 secondo prima di ritentare')
                    time.sleep(1)
                    print(f'provo a riaprire la connessione con il drogno {self.name} dopo {self.recconnectionAttempts} tentativi.')
                    self.connect()
            else:
                print('con il drogno %s ho perso le speranze' % self.ID)
                self.isReadyToFly = False
                self.exit()
        tio = 'something'
        tio = threading.Thread(target=mariconnetto)
        tio.start()
    def _connected(self, link_uri):   ##########   where a lot of things happen
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""
        print('Connected to %s' % link_uri)

        self.is_connected = True
        # The definition of the logconfig can be made before connecting
        self._lg_kalm = LogConfig(name='Stabilizer', period_in_ms=500)
        self._lg_kalm.add_variable('kalman.stateX', 'FP16')
        self._lg_kalm.add_variable('kalman.stateY', 'FP16')
        self._lg_kalm.add_variable('kalman.stateZ', 'FP16')
        self._lg_kalm.add_variable('kalman.varPX', 'FP16')
        self._lg_kalm.add_variable('kalman.varPY', 'FP16')
        self._lg_kalm.add_variable('kalman.varPZ', 'FP16')
        self._lg_kalm.add_variable('stabilizer.yaw', 'FP16')
        # The fetch-as argument can be set to FP16 to save space in the log packet
        self._lg_kalm.add_variable('pm.vbat', 'FP16')
        # Adding the configuration cannot be done until a Crazyflie is
        # connected, since we need to check that the variables we
        # would like to log are in the TOC.
        try:
            self._cf.log.add_config(self._lg_kalm)
            # This callback will receive the data
            self._lg_kalm.data_received_cb.add_callback(self._stab_log_data)
            # This callback will be called on errors
            self._lg_kalm.error_cb.add_callback(self._stab_log_error)
            self._lg_kalm.start()
 
        except KeyError as e:
            print('Could not start log configuration,'
                  '{} not found in TOC'.format(str(e)))
        except AttributeError:
          print('Could not add log config, bad configuration.')
        print('il clero')
         
        # time.sleep(0.3)
        self.reset_estimator()

        self._cf.param.set_value('commander.enHighLevel', '1')
        self._cf.param.set_value('ring.effect', '14')
        self._cf.param.set_value('lighthouse.method', '0')

        self.HLCommander = self._cf.high_level_commander
        self.positionHLCommander = PositionHlCommander(
            self._cf,
            x=self.x, y=self.y, z=0.0,
            default_velocity=0.5,
            default_height=DEFAULT_HEIGHT,
            controller=PositionHlCommander.CONTROLLER_PID) 
        time.sleep(0.3)
        self.batteryThread.start()
        self._cf.param.set_value('ring.fadeTime', RING_FADE_TIME)

        self.statoDiVolo = 'landed'
        
    def _stab_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print('Error when logging %s: %s' % (logconf.name, msg))

    def _stab_log_data(self, timestamp, data, logconf):  #riceve il feedback dei sensori e registra i dati
        # self.x              = float(data['stateEstimate.x'])
        # self.y              = float(data['stateEstimate.y'])
        # self.z              = float(data['stateEstimate.z'])
        self.x                 = float(data['kalman.stateX'])
        self.y                 = float(data['kalman.stateY'])
        self.z                 = float(data['kalman.stateZ'])
        # self.yaw            = float(data['stabilizer.yaw'])
        self.batteryVoltage    = str(round(float(data['pm.vbat']),2))
        self.kalman_VarX       = float(data['kalman.varPX'])
        self.kalman_VarY       = float(data['kalman.varPY'])
        self.kalman_VarZ       = float(data['kalman.varPZ'])
        self.isReadyToFly      = self.evaluateFlyness()
        if FEEDBACK_ENABLED and not self.isKilled and not self.exitFlag.is_set():
            try:
                self.multiprocessConnection.send([self.ID, self.x, self.y, self.z, self.batteryVoltage])
                # print('carlo')
            except ConnectionRefusedError:
                print('oooo')
    def evaluateFlyness(self):
        if  abs(self.x) > BOX_X or abs(self.y) > BOX_Y or self.z > BOX_Y:
             return False
        elif self.kalman_VarX > 0.01 or self.kalman_VarZ > 0.01 or self.kalman_VarZ > 0.01:
             return False
        else:
            return True

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the specified address)"""
        print('Connessione la drogno %s fallita: %s' % (self.ID, msg))
        self.is_connected = False
        self.isReadyToFly = False

        self.statoDiVolo = 'sconnesso'
        # self._cf.close_link()
        # time.sleep(1)
        # self.reconnect()
        # self.exit()

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print('Me son perso %s dice: %s' % (link_uri, msg))
        self.is_connected = False
        self.statoDiVolo = 'sconnesso'
        self.isReadyToFly = False

        # self._cf.close_link()
        # time.sleep(1)
        # self.reconnect()
        # self.exit()

    def _disconnected(self, link_uri):
        if self.is_connected == True:
            """Callback when the Crazyflie is disconnected (called in all cases)"""
            print('Deh, son sconnesso da %s' % link_uri)
            self.is_connected = False
            self.statoDiVolo  = 'sconnesso'
            self.isReadyToFly = False

            # self._cf.close_link()
            # time.sleep(1)
            # self.reconnect()
            # self.exit()
 
    #################################################################### movement

    def takeoff(self, height=DEFAULT_HEIGHT, time=1.5):
        print('like, now')
        if self.WE_ARE_FAKING_IT:
            time.delay(1)
            self.statoDiVolo = 'decollato!'
            self.isFlying  = True
        else:
            print('for real')
            self.reset_estimator()

            if self.isReadyToFly:
                self.starting_x  = self.x
                self.starting_y  = self.y
                self.statoDiVolo = 'scrambling!'
                self.HLCommander.takeoff(DEFAULT_HEIGHT, 2)
                # self.positionHLCommander.take_off()
                self.statoDiVolo = 'hovering'
                self.isFlying    = True
            else:
                print('BUT NOT READY')

    def land(self, speed=0.15, landing_height=0.03):
        def landing_sequence():
            self._cf.high_level_commander.land(0.0, 2.0)
            self.isFlying     = False
            time.sleep(3)
            self.isReadyToFly = True
            self.statoDiVolo = 'landed'

        if self.WE_ARE_FAKING_IT:
            self.statoDiVolo = 'landing'
            time.sleep(1)
            self.isReadyToFly = self.evaluateFlyness()
            self.statoDiVolo = 'landed'
        else:
            if self.isFlying:
                print('%s atterra! ' % self.name)
                self.statoDiVolo = 'landing'
                ld = threading.Thread(target=landing_sequence).start()
                # ld.join()
            else:
                print('%s can\'t land! (not flying)' % self.name)

    def goTo(self,x,y,z, yaw=0, duration=COMMANDS_FREQUENCY):  #la zeta è in alto!
        self.goToCount += 1

        if self.isFlying:
            # if x > 0 and y > 0:
            #     yaw = -45
            # elif x > 0 and y < 0:
            #     yaw =  45
            # elif x < 0 and y < 0:
            #     yaw =  135
            # elif x < 0 and y > 0:
            #     yaw =  135

            # clamp(x, -BOX_X, BOX_X)
            # clamp(y, -BOX_Y, BOX_Y)
            # clamp(z, 0.3   , BOX_Z)
            # print('%s va a %s %s %s girato a %s' % (self.name,  x,y,z, yaw))
            self.statoDiVolo = 'moving'
            self._cf.high_level_commander.go_to(x,y,z, yaw,1)
            # self._cf.high_level_commander.go_to
            self.statoDiVolo = 'hovering'
        # else:
            # print('perhaps take off?')

    def goLeft(self, quanto=0.3):
        if self.isFlying:
            newX = float(self.x) - float(quanto)
            print('va bene, vado a %s' % newX)
            self._cf.high_level_commander.go_to(newX, self.y, self.z, 0, 1)
            self.statoDiVolo = 'hovering'
            
    def goRight(self, quanto=0.3):
        if self.isFlying:
            newX = float(self.x) + float(quanto)
            print('va bene, vado a %s' % newX)
            self._cf.high_level_commander.go_to(newX, self.y, self.z, 0, 1)
            self.statoDiVolo = 'hovering'

    def goForward(self, quanto=0.3):
        if self.isFlying:
            newY = float(self.y) + float(quanto)
            print('va bene, vado a %s' % newY)
            self._cf.high_level_commander.go_to(self.x, newY, self.z, 0, 1)
            self.statoDiVolo = 'hovering'

    def goBack(self, quanto=0.3):
        if self.isFlying:
            newY = float(self.y) - float(quanto)
            print('va bene, vado a %s' % newY)
            self._cf.high_level_commander.go_to(self.x, newY, self.z, 0, 1)
            # self.positionHLCommander.go_to(self.x, newY, self.z, 0, 1)
            self.statoDiVolo = 'hovering'

    def goHome(self, speed=0.5):
        if self.isFlying:                
            # self._cf.high_level_commander.go_to(self.starting_x,self.starting_y,1, 0, 1)
            self._cf.high_level_commander.go_to(0,0,1, 0, 1)
        print(Fore.LIGHTCYAN_EX + 'Guys, I\'m %s, and I\'m gonna go home to %s %s' % (self.name, self.starting_x, self.starting_y ) )
    
    def goToStart(self, speed=0.5):
        if self.isFlying:                
            self._cf.high_level_commander.go_to(self.starting_x,self.starting_y,1.2, 0, 2, False)
            # self._cf.high_level_commander.go_to(0,0,1, 0, 1)
        print(Fore.LIGHTCYAN_EX + 'Guys, I\'m %s, and I\'m gonna get a fresh start to %s %s' % (self.name, self.starting_x, self.starting_y ) )

    def setRingColor(self, r, g, b, speed=0.25):
        r *= self.ringIntensity
        g *= self.ringIntensity
        b *= self.ringIntensity
        # print('how fancy would it be to drone %s to look %s?' % (self.name, [r, g, b] ))
        
        # color =  hex(int(r)) + hex(int(g)) + hex(int(b))
        # color = hex((int(r) << 16) | (int(g) << 8) | int(b))
        color = '0x'
        color += str ( hex ( int(r) ) ) [2:].zfill(2)
        color += str ( hex ( int(g) ) ) [2:].zfill(2)
        color += str ( hex ( int(b) ) ) [2:].zfill(2)

        # print ('vado al colore %s' % (color))

        self._cf.param.set_value('ring.fadeColor', color)
        # time.sleep(speed)

    def alternativeSetRingColor(self, rgb ):
        r = int( rgb[0] / 255 * 100 )
        g = int( rgb[1] / 255 * 100 )
        b = int( rgb[2] / 255 * 100 )

        self._cf.param.set_value('ring.solidRed',  '{}'.format(r))
        self._cf.param.set_value('ring.solidGreen','{}'.format(g))
        self._cf.param.set_value('ring.solidBlue', '{}'.format(b))
        print ('vado al colore %s %s %s' % (r,g, b))

    def go(self, sequenceNumber=0):
        if self.isFlying:
            if self.WE_ARE_FAKING_IT:
                self.statoDiVolo = 'sequenza simulata!'
            else:
                trajectory_id = sequenceNumber
                self.statoDiVolo = 'sequenza ' + str(sequenceNumber)
                # duration = self.upload_trajectory(trajectory_id, figure8)
                # if sequenceNumber == 0:
                #     duration = self.upload_trajectory(trajectory_id, self.lastTrajectory)
                # else:
                #     duration = self.upload_trajectory(trajectory_id, figure8)

                print ('eseguo la sequenza %s lunga %s' % (sequenceNumber, self.currentTrajectoryLenght))
                self.run_sequence(trajectory_id)
        else:
            print('not ready!')
    def run_sequence(self, trajectory_id):
        commander = self._cf.high_level_commander
        commander.takeoff(1.0, 2.0)
        time.sleep(3.0)
        relative = True
        commander.start_trajectory(trajectory_id, 1.0, relative)
        # commander.start_compressed
        time.sleep(self.currentTrajectoryLenght)
        commander.land(0.0, 4.0)
        time.sleep(4)
        # commander.stop()
 
    def startTest(self,sequenceNumber=0,loop=False):
        print ('orcodo %d'% sequenceNumber)
        def sequenzaZero():
            print('Drogno: %s. Inizio ciclo decollo/atterraggio di test' % self.ID)
            # input("enter to continue")
            self.alternativeSetRingColor([255,0,0])
            self.positionHLCommander.go_to(self.starting_x, self.starting_y, 0.5, 0.2)
            self.alternativeSetRingColor([255,255,0])
            self.positionHLCommander.go_to(self.starting_x, self.starting_y, 1.0, 0.2)
            self.alternativeSetRingColor([255,255,255])

            self.positionHLCommander.go_to(self.starting_x, self.starting_y, 0.5, 0.2)
            
            print('Drogno: %s. Fine ciclo decollo/atterraggio di test' % self.ID)
            self.statoDiVolo = 'landed'
            if loop:
                self.sequenzaTest(sequenceNumber,loop)
            else:
                print(self.HLCommander._cf.state)
        def sequenzaUno():
            print('inizio prima sequenza di test')
            self.positionHLCommander.go_to(0.0, 0.0, 1)
            self.setRingColor(255,   0,   0)
            time.sleep(1)

            self.positionHLCommander.go_to(0.0, 1, 1, 0.2)
            self.setRingColor(255,   0,   0)

            self.positionHLCommander.go_to(1, 1, 1, 0.2)
            self.setRingColor(  0, 255,  0)
            
            self.positionHLCommander.go_to(1.0, 0.0, 1, 0.2)
            self.setRingColor(  0,   0, 255)

            self.positionHLCommander.go_to(0.0, 0.0, 1, 0.2)
            self.setRingColor(255, 255,   0)
            time.sleep(1)

            self.setRingColor(255, 0,   0)
            time.sleep(1)
            self.setRingColor(0, 255,   0)
            time.sleep(1)
            self.setRingColor(0, 0,   255)
            time.sleep(1)

            self.setRingColor(0, 255,   255)
            time.sleep(1)
            self.setRingColor(255, 255,   0)
            time.sleep(1)
            self.setRingColor(255, 0,   255)
            time.sleep(1)
            
            print('fine prima sequenza di test')
            self.statoDiVolo = 'hovering'
        def sequenzaDue():
            pass
        def sequenzaTre():
            print('Drogno: %s. Inizioquadrato di test' % self.ID)
            # input("enter to continue")
            self.positionHLCommander.go_to(0.0, 0.0, 0.5, 0.2)
            self.positionHLCommander.go_to(0.0, 0.0, 1.0, 0.2)
            self.positionHLCommander.go_to(0.0, 0.0, 0.5, 0.2)
            self.positionHLCommander.land()
            print('Drogno: %s. Fine ciclo decollo/atterraggio di test' % self.ID)
            self.statoDiVolo = 'landed'
        def sequenzaQuattro():
            print('Drogno: %s. Inizio test a set pointsss' % self.ID)
            self._cf.commander.send_position_setpoint(0.5, 0.5, 1, 30)
            time.sleep(1)
            self._cf.commander.send_position_setpoint(0.5, -0.5, 1, -30)
            time.sleep(1)
            self._cf.commander.send_position_setpoint(-0.5, -0.5, 1, -90)
            time.sleep(1)
            self._cf.commander.send_position_setpoint(0.5, -0.5, 1, -130)
            time.sleep(1)
            self._cf.commander.send_position_setpoint(0.5, 0.5, 1, -270)
            time.sleep(1)
            self._cf.commander.send_position_setpoint(0.0, 0.0, 1, 180)
            # self._cf.commander.set_client_xmode()
            time.sleep(0.1)
            # self.positionHLCommander.land()
            # self._cf.commander.send_stop_setpoint()
            self.statoDiVolo = 'landed'

        sequenzeTest = [sequenzaZero, sequenzaUno, sequenzaDue, sequenzaTre, sequenzaQuattro]
        if self.isFlying:
            if self.WE_ARE_FAKING_IT:
                self.statoDiVolo = 'sequenza simulata!'
            else:
                self.statoDiVolo = 'sequenza ' + str(sequenceNumber)
                print ('eseguo la sequenza %s' % sequenceNumber)
                if not self.currentSequenceThread:
                    self.currentSequenceThread = threading.Thread(target=sequenzeTest[sequenceNumber])
                    self.currentSequenceThread.start()
                    print('non ci sono sequenze in esecuzione, parto con la %s' % sequenceNumber)
                else:
                 print('la sequenza in esecuzione non può essere fermata. \nMAI')
        else:
            print('not ready!')

    def upload_trajectory(self, trajectory_id):
        trajectory_mem = self._cf.mem.get_mems(MemoryElement.TYPE_TRAJ)[0]
        print ('sì! uppa la %s'% trajectory_id)
        total_duration = 0
        for row in self.TRAJECTORIES[trajectory_id]:
            duration = row[0]
            x = Poly4D.Poly(row[1:9])
            y = Poly4D.Poly(row[9:17])
            z = Poly4D.Poly(row[17:25])
            yaw = Poly4D.Poly(row[25:33])
            trajectory_mem.poly4Ds.append(Poly4D(duration, x, y, z, yaw))
            total_duration += duration

        upload_result = Uploader().upload(trajectory_mem)
        if not upload_result:
            print('Upload failed, aborting!')
        self._cf.high_level_commander.define_trajectory(trajectory_id, 0, len(trajectory_mem.poly4Ds))
        self.currentTrajectoryLenght =  total_duration

    def evaluateBattery(self):
        while not self.exitFlag.is_set():
            # print (self.batteryVoltage)
            level = 0.0
            if self.batteryVoltage == 'n.p.':
                level = 20.
            else:
                level  = float(self.batteryVoltage)
            if level<3.50:
                print (Fore.YELLOW + 'ciao, sono il drone %s e comincio ad avere la batteria un po\' scarica (%s)' % (self.ID, level))
                self.isReadyToFly = False

            if level<3.35:
                if self.statoDiVolo == 'landed':
                    print ('ciao, sono il drone %s e sono così scarico che non posso più far nulla. (%s)' %  (self.ID, level))
                    self.statoDiVolo == 'depleted'
                    self.isReadyToFly = False

                    # self._cf.high_level_commander.stop()
                    # self._cf.commander.send_stop_setpoint()
                else:
                    print (Fore.RED + 'ciao, sono il drone %s e sono così scarico che atterrerei. (%s)' %  (self.ID, level))
                    self.land()
                    self.statoDiVolo = 'landed'
                    self.isFlying = False
                    self.isReadyToFly = False
            time.sleep(BATTERY_CHECK_RATE)

    def killMeSoftly(self):
        self.land()
        self.exit()
    def killMeHardly(self):
        # self.setRingColor(0,0,0)
        self._cf.high_level_commander.stop()
        self._cf.commander.send_stop_setpoint()
        self.exit()
    def goToSleep(self):
        PowerSwitch(self.link_uri).stm_power_down()
        self.statoDiVolo = 'stand by'
        self.standBy = True
        self.is_connected = False
    def wakeUp(self):
        PowerSwitch(self.link_uri).stm_power_up()
        self.connect()
        self.statoDiVolo = 'waking up'

    def exit(self):
        print('exitFlag is now set for drogno %s, bye kiddo' % self.name)
        self.multiprocessConnection.send('fuck you')
        self._cf.close_link()
        self.isKilled = True
        self.isReadyToFly = False
        self.exitFlag.set()

def clamp(num, min_value, max_value):
   return max(min(num, max_value), min_value)


   # The trajectory to fly
# See https://github.com/whoenig/uav_trajectories for a tool to generate
# trajectories

# Duration,x^0,x^1,x^2,x^3,x^4,x^5,x^6,x^7,y^0,y^1,y^2,y^3,y^4,y^5,y^6,y^7,z^0,z^1,z^2,z^3,z^4,z^5,z^6,z^7,yaw^0,yaw^1,yaw^2,yaw^3,yaw^4,yaw^5,yaw^6,yaw^7
figure8 = [
    [1.050000, 0.000000, -0.000000, 0.000000, -0.000000, 0.830443, -0.276140, -0.384219, 0.180493, -0.000000, 0.000000, -0.000000, 0.000000, -1.356107, 0.688430, 0.587426, -0.329106, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.710000, 0.396058, 0.918033, 0.128965, -0.773546, 0.339704, 0.034310, -0.026417, -0.030049, -0.445604, -0.684403, 0.888433, 1.493630, -1.361618, -0.139316, 0.158875, 0.095799, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.620000, 0.922409, 0.405715, -0.582968, -0.092188, -0.114670, 0.101046, 0.075834, -0.037926, -0.291165, 0.967514, 0.421451, -1.086348, 0.545211, 0.030109, -0.050046, -0.068177, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.700000, 0.923174, -0.431533, -0.682975, 0.177173, 0.319468, -0.043852, -0.111269, 0.023166, 0.289869, 0.724722, -0.512011, -0.209623, -0.218710, 0.108797, 0.128756, -0.055461, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.560000, 0.405364, -0.834716, 0.158939, 0.288175, -0.373738, -0.054995, 0.036090, 0.078627, 0.450742, -0.385534, -0.954089, 0.128288, 0.442620, 0.055630, -0.060142, -0.076163, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.560000, 0.001062, -0.646270, -0.012560, -0.324065, 0.125327, 0.119738, 0.034567, -0.063130, 0.001593, -1.031457, 0.015159, 0.820816, -0.152665, -0.130729, -0.045679, 0.080444, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.700000, -0.402804, -0.820508, -0.132914, 0.236278, 0.235164, -0.053551, -0.088687, 0.031253, -0.449354, -0.411507, 0.902946, 0.185335, -0.239125, -0.041696, 0.016857, 0.016709, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.620000, -0.921641, -0.464596, 0.661875, 0.286582, -0.228921, -0.051987, 0.004669, 0.038463, -0.292459, 0.777682, 0.565788, -0.432472, -0.060568, -0.082048, -0.009439, 0.041158, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.710000, -0.923935, 0.447832, 0.627381, -0.259808, -0.042325, -0.032258, 0.001420, 0.005294, 0.288570, 0.873350, -0.515586, -0.730207, -0.026023, 0.288755, 0.215678, -0.148061, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [1.053185, -0.398611, 0.850510, -0.144007, -0.485368, -0.079781, 0.176330, 0.234482, -0.153567, 0.447039, -0.532729, -0.855023, 0.878509, 0.775168, -0.391051, -0.713519, 0.391628, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
]
figure8Triple = [
    [1.050000, 0.000000, -0.000000, 0.000000, -0.000000, 0.830443, -0.276140, -0.384219, 0.180493, -0.000000, 0.000000, -0.000000, 0.000000, -1.356107, 0.688430, 0.587426, -0.329106, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.710000, 0.396058, 0.918033, 0.128965, -0.773546, 0.339704, 0.034310, -0.026417, -0.030049, -0.445604, -0.684403, 0.888433, 1.493630, -1.361618, -0.139316, 0.158875, 0.095799, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.620000, 0.922409, 0.405715, -0.582968, -0.092188, -0.114670, 0.101046, 0.075834, -0.037926, -0.291165, 0.967514, 0.421451, -1.086348, 0.545211, 0.030109, -0.050046, -0.068177, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.700000, 0.923174, -0.431533, -0.682975, 0.177173, 0.319468, -0.043852, -0.111269, 0.023166, 0.289869, 0.724722, -0.512011, -0.209623, -0.218710, 0.108797, 0.128756, -0.055461, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.560000, 0.405364, -0.834716, 0.158939, 0.288175, -0.373738, -0.054995, 0.036090, 0.078627, 0.450742, -0.385534, -0.954089, 0.128288, 0.442620, 0.055630, -0.060142, -0.076163, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.560000, 0.001062, -0.646270, -0.012560, -0.324065, 0.125327, 0.119738, 0.034567, -0.063130, 0.001593, -1.031457, 0.015159, 0.820816, -0.152665, -0.130729, -0.045679, 0.080444, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.700000, -0.402804, -0.820508, -0.132914, 0.236278, 0.235164, -0.053551, -0.088687, 0.031253, -0.449354, -0.411507, 0.902946, 0.185335, -0.239125, -0.041696, 0.016857, 0.016709, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.620000, -0.921641, -0.464596, 0.661875, 0.286582, -0.228921, -0.051987, 0.004669, 0.038463, -0.292459, 0.777682, 0.565788, -0.432472, -0.060568, -0.082048, -0.009439, 0.041158, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.710000, -0.923935, 0.447832, 0.627381, -0.259808, -0.042325, -0.032258, 0.001420, 0.005294, 0.288570, 0.873350, -0.515586, -0.730207, -0.026023, 0.288755, 0.215678, -0.148061, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [1.053185, -0.398611, 0.850510, -0.144007, -0.485368, -0.079781, 0.176330, 0.234482, -0.153567, 0.447039, -0.532729, -0.855023, 0.878509, 0.775168, -0.391051, -0.713519, 0.391628, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [1.050000, 0.000000, -0.000000, 0.000000, -0.000000, 0.830443, -0.276140, -0.384219, 0.180493, -0.000000, 0.000000, -0.000000, 0.000000, -1.356107, 0.688430, 0.587426, -0.329106, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [1.053185, -0.398611, 0.850510, -0.144007, -0.485368, -0.079781, 0.176330, 0.234482, -0.153567, 0.447039, -0.532729, -0.855023, 0.878509, 0.775168, -0.391051, -0.713519, 0.391628, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.560000, 0.405364, -0.834716, 0.158939, 0.288175, -0.373738, -0.054995, 0.036090, 0.078627, 0.450742, -0.385534, -0.954089, 0.128288, 0.442620, 0.055630, -0.060142, -0.076163, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.560000, 0.001062, -0.646270, -0.012560, -0.324065, 0.125327, 0.119738, 0.034567, -0.063130, 0.001593, -1.031457, 0.015159, 0.820816, -0.152665, -0.130729, -0.045679, 0.080444, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    [0.700000, -0.402804, -0.820508, -0.132914, 0.236278, 0.235164, -0.053551, -0.088687, 0.031253, -0.449354, -0.411507, 0.902946, 0.185335, -0.239125, -0.041696, 0.016857, 0.016709, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],  # noqa
    ]

class Uploader:
    def __init__(self):
        self._is_done = False
        self._sucess = True

    def upload(self, trajectory_mem):
        print('Uploading data')
        trajectory_mem.write_data(self._upload_done,
                                  write_failed_cb=self._upload_failed)

        while not self._is_done:
            time.sleep(0.2)

        return self._sucess

    def _upload_done(self, mem, addr):
        print('Data uploaded')
        self._is_done = True
        self._sucess = True

    def _upload_failed(self, mem, addr):
        print('Data upload failed')
        self._is_done = True
        self._sucess = False