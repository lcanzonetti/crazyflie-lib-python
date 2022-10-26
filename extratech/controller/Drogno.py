#rf 2022

import time, sys, os, threading, multiprocessing
from   datetime import datetime
from   multiprocessing.connection import Client
from   colorama             import Fore, Back, Style
from   colorama             import init as coloInit
coloInit(convert=True)

import GLOBALS as GB
import OSC_feedabcker 
import trajectories
import logger_manager
import common_utils
from trajectories import sequenze_test

#crazyflie's
import logging
from   cflib.crazyflie                            import Crazyflie
from   cflib.positioning.position_hl_commander    import PositionHlCommander
from   cflib.positioning.motion_commander         import MotionCommander
from   cflib.crazyflie.mem                        import MemoryElement
from   cflib.utils.power_switch                   import PowerSwitch
from   cflib                                      import crtp as radio
class Drogno(threading.Thread):
    def __init__(self, ID, link_uri, lastRecordPath):
        threading.Thread.__init__(self)
        #####################################  identity
        self.cache_location         = os.path.join(GB.ROOT_DIR, 'crazyflies_cache', self.name)
        self._cf                    = Crazyflie(rw_cache=self.cache_location)
        self.link_uri               = link_uri
        self.ID                     = int(ID)
        self.name                   = 'Drogno_'+str(ID)
        #####################################  threadsss
        self.connectionThread       = None
        self.killingPill            = threading.Event()
        self.controlThread          = False
        self.printThread            = False
        self.loggingThread          = False
        self.current_sequence       = None
        self.currentSequenceThread  = None
        self.currentSequence_killingPill = threading.Event()
        self.recconnectionAttempts  = 0
        #####################################  statusss
        self.is_connected           = False
        self.still_have_hope_to_reconnect = True
        self.standBy                = False
        self.isPositionEstimated    = False
        self.statoDiVolo            = 'starting'
        self.isKilled               = False
        self.isReadyToFly           = False
        self.isEngaged              = True
        self.isFlying               = False
        self.isTumbled              = False
        self.linkQuality            = 0
        self.batteryVoltage         = 'n.p.'
        self.batteryStatus          = 2
        #####################################  position
        self.positionHLCommander    = None 
        self.x           = self.y           = self.z           = self.yaw = 0.0
        self.starting_x  = self.starting_y  = self.starting_z  = 0.0
        self.kalman_VarX = self.kalman_VarY = self.kalman_VarZ = 0
        self.requested_X = self.requested_Y = self.requested_Z = 0.0
        self.requested_R = self.requested_G = self.requested_B = 0
        self.prefStartPoint_X, self.prefStartPoint_Y = GB.PREFERRED_STARTING_POINTS[self.ID][0], GB.PREFERRED_STARTING_POINTS[self.ID][1]
        #####################################  initial testss
        self.batterySag             = 0.50 # sta carica
        self.isBatterytestPassed    = False
        self.motorPass              = [1,1,1,1]
        #####################################  counterssss
        self.commandsCount          = 0.0
        self.connection_time        = None
        self.scramblingTime         = None
        self.flyingTime             = 0
        self.ledMem                 = 0
        self.esteemsCount           = 0
        #####################################  trajextoriesss
        # self.lastRecordPath  = lastRecordPath
        # self.lastTrajectory  = ''
        self.TRAJECTORIES    = {}
        # self.currentTrajectoryLenght = 0
        ################################              Connect some callbacks from the Crazyflie API
        self._cf.connected.add_callback        (self._connected)
        self._cf.param.all_updated.add_callback(self._all_params_there) 
        self._cf.fully_connected.add_callback  (self._fully_connected)
        self._cf.disconnected.add_callback     (self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback  (self._connection_lost)
        ################################                 Feedback instance in his own process
        self.multiprocessConnection    = None
        self.feedbacker_receiving_port = 9100 + self.ID
        self.feedbacker_address        = ('127.0.0.1', self.feedbacker_receiving_port)
        self.feedbacker                = OSC_feedabcker.Feedbacco(self.ID, GB.eventi.get_process_exit_event(), self.feedbacker_receiving_port  )
        self.feedbackProcess           = multiprocessing.Process(name=self.name+'_feedback',target=self.feedbacker.start, daemon=True).start()
        ################################################## logging
        self.logger_manager = logger_manager.Logger_manager(self, self._cf, self.ID)
        if (GB.FILE_LOGGING_ENABLED):
            now = datetime.now() # current date and time
            date_time = now.strftime("%m_%d_%Y__%H_%M_%S")
            logName = os.path.join(GB.ROOT_DIR, 'drognoLogs', (self.name + "_" +date_time + ".log"))
            os.makedirs(os.path.dirname(logName), exist_ok=True)
            # annulla_LOG = logging.getLogger()
            # annulla_LOG.setLevel(logging.INFO)
            self.LoggerObject = logging.getLogger(__name__)
            self.LoggerObject.propagate = False
            self.LoggerObject.setLevel(logging.DEBUG)
            self.formatter    = logging.Formatter('%(levelname)s: %(asctime)s %(funcName)s(%(lineno)d) -- %(message)s', datefmt = '%d-%m-%Y %H:%M:%S')
            self.file_handler = logging.FileHandler(logName, mode="w", encoding=None, delay=False)
            self.file_handler.setFormatter(self.formatter)
            self.LoggerObject.addHandler(self.file_handler)
            self.LoggerObject.info('This is drone log from %s' % self.name)
    ##  here trajectories are loaded from separate file or from trajectory module, then Feedback is instantiated and connection is started
    def run(self):
        print (Fore.LIGHTBLUE_EX + "starting " + self.name + " class instance")
        try:
            self.TRAJECTORIES [0] = GB.lastRecordPath + '/trajectory_' + str(self.ID) + '.txt'
            self.TRAJECTORIES [7] = trajectories.figure8Triple
            self.TRAJECTORIES [8] = trajectories.figure8
            print ('there are %s trajectories' % len(self.TRAJECTORIES) )
            with open(self.TRAJECTORIES[0], 'r') as t:
                print(t.readlines())
                self.lastTrajectory = t.readlines()
        except FileNotFoundError as ff:
            print(ff)
        except Exception as e:
            print('loading trajectories encountered an issue:\n%s' % e)

        connectedToFeedback = False
        if GB.FEEDBACK_ENABLED :
        # if GB.FEEDBACK_ENABLED and not GB.eventi.get_thread_exit_event().is_set():
            time.sleep(0.4)
            while not connectedToFeedback:
                try:
                    time.sleep(0.2)
                    self.multiprocessConnection = Client(self.feedbacker_address)
                    connectedToFeedback = True
                except ConnectionRefusedError:
                    print('server del drogno %s feedback non ancora connesso!' % self.ID)
        if GB.PRINTING_ENABLED    : self.printThread     = threading.Thread(target=self.logger_manager.print_status).start()
        if GB.FILE_LOGGING_ENABLED: self.loggingThread   = threading.Thread(target=self.log_status).start()
        self.connect()
                    
    def activate_mellinger_controller(self, use_mellinger):
        controller = 1
        if use_mellinger:
            controller = 2
        self._cf.param.set_value('stabilizer.controller', controller)

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

    def resetEstimator(self):
        self.x = self.starting_x
        self.y = self.starting_y
        self.z = 0
        self._cf.param.set_value('kalman.resetEstimation', '1')
        time.sleep(0.5)
        self._cf.param.set_value('kalman.resetEstimation', '0')
        print(Fore.MAGENTA + 'estimator reset done on ' + self.name)

    #################################################################### connection
    def connect(self):
        if not GB.WE_ARE_FAKING_IT:   ## true life
            if self.isKilled == False:
                print(f'Provo a connettermi al drone { self.ID} all\'indirizzo { self.link_uri}    ')

                def connection():
                    self.statoDiVolo = 'connecting'
                    try:
                        self._cf.open_link(self.link_uri)
                        self.connection_time = time.time()
                        while not self.killingPill.is_set() and not self.is_connected:
                            for cursor in '\\|/-':
                                # print('...in connessione...')
                                time.sleep(0.1)
                                # Use '\r' to move cursor back to line beginning
                                # Or use '\b' to erase the last character
                                sys.stdout.write('\r{}'.format(cursor))
                                # Force Python to write data into terminal.
                                sys.stdout.flush()
                    except IndexError:
                        print('capperi')
                    except Exception as e:
                        print('not connected--->%s'%e)
                self.connectionThread = threading.Thread(target=connection).start()
        else:  ## fake world
            time.sleep(1)
            self._connected(self.link_uri)
            time.sleep(1)
            self._fully_connected(self.link_uri)           

    def reconnect(self):
        # def mariconnetto():
        #     self.still_have_hope_to_reconnect = True
        #     while self.still_have_hope_to_reconnect:
        #         if self.recconnectionAttempts == 0:
        #             print(f'provo a riaprire la connessione con il drogno {self.name}')
        #             self.recconnectionAttempts+=1
        #             self.statoDiVolo = 'connecting'
        #             self.connect()
        #         elif self.recconnectionAttempts >= 1 and self.recconnectionAttempts < 10:
        #             self.recconnectionAttempts +=1
        #             print('Aspetto 3 secondi prima di ritentare')
        #             time.sleep(3)
        #             print(f'provo a riaprire la connessione con il drogno {self.name} dopo {self.recconnectionAttempts} tentativi.')
        #             self.connect()
        #         else:
        #             print('con il drogno %s ho perso le speranze' % self.ID)
        #             self.still_have_hope_to_reconnect = False
        # tio = threading.Thread(name=self.name+'_reconnectThread',target=mariconnetto)
        # tio.start()
        pass

    def _connected(self, link_uri):   
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""
        print('TOC scaricata per il %s, in attesa dei parametri.' % (self.name))
        self.still_have_hope_to_reconnect = False
        
    def _all_params_there(self):
        print('Parametri scaricati per %s' % self.name)
        print(Fore.LIGHTGREEN_EX + '%s connesso, it took %s seconds'% (self.name, round(time.time()-self.connection_time,2)))
        self.is_connected = True
        # self.linkone      = radio.get_link_driver(self.link_uri)
        # print(f'linkone= {self.linkone}')
        # self.linkone.set_retries(1)
        # linkone.set_arc(1) ## retries
        # self.linkone._retry_before_disconnect = 3
        self.batteryThread = threading.Thread(name=self.name+'_batteryThread',target=self.evaluateBattery)  # perché è qui?
        self.batteryThread.start()
        self.statoDiVolo = 'landed'
    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the specified address)"""
        print('Connessione con drogno %s fallita: %s' % (self.ID, msg))
        self.is_connected = False
        self.isReadyToFly = False
        self.statoDiVolo = 'sconnesso'
        self.still_have_hope_to_reconnect = True

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print('Me son perso %s dice: %s' % (link_uri, msg))
        self.is_connected = False
        self.statoDiVolo = 'sconnesso'
        self.isReadyToFly = False
        print('Me son perso %s dice: %s' % (link_uri, msg))
        if not self.statoDiVolo == 'connecting':  self.reconnect()

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected (called in all cases)"""
        print('Deh, son sconnesso da %s' % link_uri)
        self.is_connected = False
        self.statoDiVolo  = 'sconnesso'
        self.isReadyToFly = False
        if not self.standBy and not self.isKilled and not self.statoDiVolo == 'connecting':  self.reconnect()

    ##################################################   pienamente connesso anche e non ho tutti i parametri? Il logging parte qui e si impostano i motion commanders
    def _fully_connected(self, link_uri): 
        print('Imposto il logging del drone %s ' % link_uri)
        self.logger_manager.add_log_configurations()
        self.logger_manager.set_logging_level(0) ## start

        if not GB.WE_ARE_FAKING_IT:                        #### Se stiamo facendo finta non proviamo a comunicare con un drone che non esiste!
            return
    
        self._cf.param.set_value('commander.enHighLevel', '1')
        if GB.INITIAL_TEST: 
            self._cf.param.set_value('health.startBatTest', '1')
            self._cf.param.set_value('health.startPropTest', '1')
        
        self.ledMem = self._cf.mem.get_mems(MemoryElement.TYPE_DRIVER_LED)
        self._cf.param.set_value('ring.effect', '13')     #solid color? Missing docs?
        self._cf.param.set_value('ring.fadeTime', GB.RING_FADE_TIME)
        self.setRingColor(0,0,255)

        self._cf.param.set_value('lighthouse.method', GB.LIGHTHOUSE_METHOD)

        self.positionHLCommander = PositionHlCommander(
            self._cf,
            x=self.x, y=self.y, z=0.0,
            default_velocity=GB.DEFAULT_VELOCITY,
            default_height=GB.DEFAULT_HEIGHT,
            controller=PositionHlCommander.CONTROLLER_PID) 

        self.motionCommander = MotionCommander(
            self._cf,
            default_height=1.0
        )
        self.resetEstimator()
        self.isReadyToFly = self.evaluateFlyness()
       
    def evaluateFlyness(self):
        if GB.WE_ARE_FAKING_IT:
            self.statoDiVolo = 'ready'
            return True

        if self.is_connected and not self.standBy:
            if  abs(self.x) > GB.BOX_X or abs(self.y) > GB.BOX_Y or self.z > GB.BOX_Y or self.isTumbled:
                self.statoDiVolo = 'out of BOX'
                self._cf.param.set_value('ring.effect', '11')  #alert
                return False
            elif abs(self.x) > 10 or abs(self.y) > 10 or abs(self.x) > 5:
                print(Fore.RED + 'drone %s is way way off, resetting kalman...' % self.ID)
                self.statoDiVolo = 'lost'
                self.resetEstimator()
                self._cf.param.set_value('ring.effect', '11')  #alert
                return False
            elif self.kalman_VarX > 0.01 or self.kalman_VarZ > 0.01 or self.kalman_VarZ > 0.01:
                self.statoDiVolo = 'BAD kalman'
                return False
            # elif not all (self.motorPass):
            #     self.statoDiVolo = 'BAD propellers'
            #     return False
            elif not self.batterySag < 0.7:
                self.statoDiVolo = 'BAD battery!'
                return False
            elif self.batteryStatus == 3:
                self.statoDiVolo = 'LOW battery!'
                return False
            else:
                self._cf.param.set_value('ring.effect', '13')  #solid color? Missing docs?
                self.statoDiVolo = 'ready'
                return True
        else:
            # print ('nope nope nope!')
            pass
            
    def log_status(self):
        if GB.FILE_LOGGING_ENABLED:
            self.LoggerObject.info('Logger started')
            while not self.killingPill.is_set():
                time.sleep(GB.print_rate)
                if not GB.WE_ARE_FAKING_IT and self.is_connected:
                    self.LoggerObject.info(f"{self.name}: {self.statoDiVolo}\tbattery: {self.batteryVoltage}\
                    \tkalman var: {round(self.kalman_VarX,3)} {round(self.kalman_VarY,3)} {round(self.kalman_VarZ,3)}\
                    \tbatterySag: {round(self.batterySag,3)}\tlink quality: {self.linkQuality}\tflight time: {self.flyingTime}s\
                    \tpos {self.x:0.2f} {self.y:0.2f} {self.z:0.2f}\tyaw: {self.yaw:0.2f}\tmsg/s {round((self.commandsCount/GB.print_rate),1)}")
                    self.commandsCount = 0
            print('Log chiuso per %s ' % self.name)

    ####################################################################     mmmmooovement
    def takeOff(self, height=GB.DEFAULT_HEIGHT,  scrambling_duration=GB.DEFAULT_SCRAMBLING_TIME):
        def scramblingsequence():
            self.starting_x     = self.x
            self.starting_y     = self.y
            self.statoDiVolo    = 'scrambling!'
            self.scramblingTime = time.time()
            self._cf.high_level_commander.takeoff(height, scrambling_duration)
            self.isFlying       = True
            time.sleep( scrambling_duration)
            self.statoDiVolo    = 'hovering'
            self.logger_manager.set_logging_level(1)  ## sets logging level to FAST fly mode

        def fake_scramblingsequence():
            self.starting_x  = self.x
            self.starting_y  = self.y
            self.statoDiVolo = 'scrambling!'
            self.scramblingTime = time.time()
            self.isFlying    = True
            self.statoDiVolo = 'hovering'

        if GB.WE_ARE_FAKING_IT:
            scramblingThread = threading.Thread(target=fake_scramblingsequence, name=self.name+'_scramblingThread').start()
            return

        if self.isFlying:
            print('%s can\'t take off, as is already in the air!'% self.name)
            return
        if self.isReadyToFly:
            scramblingThread = threading.Thread(target=scramblingsequence, name=self.name+'_scramblingThread').start()
            print('%s SCRAMBLING!'% self.name)
        else:
            print('%s can\'t take off, not ready!'% self.name)

    def land(self, speed=2.5, landing_height=0.05,thenGoToSleep=False):
        def landing_sequence():
            try:
                self._cf.high_level_commander.land(landing_height, speed)
                time.sleep(3)
                self.isFlying     = False
                self.statoDiVolo = 'landed'
                self.logger_manager.set_logging_level(1)  ## sets logging level to landed mode

                if (thenGoToSleep): self.goToSleep()
                self.isReadyToFly = self.evaluateFlyness()
            except Exception as e:
                print('%s could not correctly complete landing procedure (%s)'%(self.name,e))
        
        def fake_landing_sequence():
            time.sleep(speed)
            self.isFlying     = False
            self.statoDiVolo = 'landed'
            if (thenGoToSleep): self.goToSleep()
            self.isReadyToFly = self.evaluateFlyness()

        if not GB.WE_ARE_FAKING_IT:
            if self.isFlying:
                print('%s atterra! ' % self.name)
                self.statoDiVolo = 'landing'
                ld = threading.Thread(name=self.name+'_landingThread',target=landing_sequence).start()
                # ld.join()
            else:
                print('%s can\'t land! (not flying)' % self.name)
        else:
            if self.isFlying:
                print('%s atterra! ' % self.name)
                self.statoDiVolo = 'landing'
                ld = threading.Thread(name=self.name+'_landingThread',target=fake_landing_sequence).start()
               
    def goTo(self,x,y,z, yaw=0, duration=0.5):  #la zeta è in alto!
        self.commandsCount += 1
        duration = GB.commandsFrequency*3
        if self.isFlying:
            if GB.CLAMPING:
                common_utils.clamp(x, -GB.BOX_X, GB.BOX_X)
                common_utils.clamp(y, -GB.BOX_Y, GB.BOX_Y)
                common_utils.clamp(z, 0.20     , GB.BOX_Z)
            # print('%s va a %s %s %s girato a %s' % (self.name,  x,y,z, yaw))
            self.statoDiVolo = 'moving'
            self._cf.high_level_commander.go_to(x,y,z, yaw,duration)
            self.statoDiVolo = 'hovering'
   
    def goLeft(self, quanto=0.3):
        if self.isFlying:
            newX = float(self.x) - float(quanto)
            self._cf.high_level_commander.go_to(newX, self.y, self.z, 0, 1)
            print('va bene, vado a %s' % newX)
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
            self.statoDiVolo = 'moving'
            self._cf.high_level_commander.go_to(self.x, newY, self.z, 0, 1)
            self.statoDiVolo = 'hovering'
    def goUp(self, quanto=0.3):
        if self.isFlying:
            newZ = float(self.z) + float(quanto)
            print('va bene, salgo a %s' % newZ)
            self.statoDiVolo = 'moving'
            self._cf.high_level_commander.go_to(self.x, self.y, newZ, 0, 1)
            self.statoDiVolo = 'hovering'
    def goDown(self, quanto=0.3):
        if self.isFlying:
            newZ = float(self.z) - float(quanto)
            print('va bene, scendo a %s' % newZ)
            self.statoDiVolo = 'moving'
            self._cf.high_level_commander.go_to(self.x, self.y, newZ, 0, 1)
            self.statoDiVolo = 'hovering'

    def goHome(self, speed=0.5):
        if self.isFlying:                
            self._cf.high_level_commander.go_to(0,0,1, 0, 1)
        print(Fore.LIGHTCYAN_EX + 'Guys, I\'m %s, and I\'m gonna go home to %s %s' % (self.name, self.starting_x, self.starting_y ) )
    
    def goToStart(self, speed=0.5):
        if self.isFlying:                
            self._cf.high_level_commander.go_to(self.starting_x,self.starting_y,1.5, 180, 2, False)
        print(Fore.LIGHTCYAN_EX + 'Guys, I\'m %s, and I\'m gonna get a fresh start toward %s %s' % (self.name, self.starting_x, self.starting_y ) )
  
    def testSequence(self,requested_sequenceNumber):

        print('startTestSequence con la sequenza %s, attualmente e\' in esecuzione la %s' % (requested_sequenceNumber, self.current_sequence))
        if GB.WE_ARE_FAKING_IT:
            self.statoDiVolo = 'sequenza simulata!'
            return
        ## se nessuna sequenza in volo parte la scelta
        if self.current_sequence is None and requested_sequenceNumber <= len (sequenze_test):
            self.currentSequence_killingPill.clear()
            self.statoDiVolo = 'sequenza_' + str(requested_sequenceNumber)
            print ('eseguo la sequenza %s' % requested_sequenceNumber)
            self.current_sequence       = requested_sequenceNumber
            self.currentSequenceThread  = threading.Thread(target=sequenze_test[requested_sequenceNumber-1],args=[self] ,daemon=True,).start()

        ## se in volo la stessa la si stoppa
        elif requested_sequenceNumber == self.current_sequence:
            self.currentSequence_killingPill.set()
            print('stoppo la sequenza test' + requested_sequenceNumber)
            self.current_sequence = None

        ## se in volo un'altra la si cambia
        elif requested_sequenceNumber != self.current_sequence and requested_sequenceNumber <= len (sequenze_test):
            self.currentSequence_killingPill.set()
            print('stoppo la sequenza test' + requested_sequenceNumber)
            self.current_sequence = None
    ####################################################################     management

    def setRingColor(self, vr, vg, vb, speed=0.25):
        self.commandsCount += 1

        self.requested_R    = vr
        self.requested_G    = vg
        self.requested_B    = vb

        vr = int(vr * GB.RING_INTENSITY)
        vg = int(vg * GB.RING_INTENSITY)
        vb = int(vb * GB.RING_INTENSITY)
        # print ('vado al colore %s' % (vr, vg, vb))

        if len(self.ledMem) > 0:
            self.ledMem[0].leds[10].set(r=vr, g=vg, b=vb)
            self.ledMem[0].leds[9].set(r=vr, g=vg, b=vb)
            self.ledMem[0].leds[7].set(r=vr, g=vg, b=vb)
            self.ledMem[0].leds[6].set(r=vr, g=vg, b=vb)
            self.ledMem[0].leds[4].set(r=vr, g=vg, b=vb)
            self.ledMem[0].leds[3].set(r=vr, g=vg, b=vb)
            self.ledMem[0].leds[1].set(r=vr, g=vg, b=vb)
            self.ledMem[0].leds[0].set(r=vr, g=vg, b=vb)
            self.ledMem[0].write_data(None)
    def alternativeSetRingColor(self, rgb ):
        r = int( rgb[0] / 255 * 100 )
        g = int( rgb[1] / 255 * 100 )
        b = int( rgb[2] / 255 * 100 )

        self._cf.param.set_value('ring.solidRed',  '{}'.format(r))
        self._cf.param.set_value('ring.solidGreen','{}'.format(g))
        self._cf.param.set_value('ring.solidBlue', '{}'.format(b))
        print ('vado al colore %s %s %s' % (r,g, b))

    def evaluateBattery(self):
        while not self.killingPill.is_set() and not GB.eventi.get_process_exit_event().is_set() and self.is_connected:
            ### non so se  questo è il posto giusto per 'sta roba ma almeno è l'unico thread a venire sempre eseguito:
            if not self.scramblingTime == None and self.isFlying:
                self.flyingTime = int(time.time() - self.scramblingTime)
            else:
                self.flyingTime = 0
            print(f'flying time: {self.flyingTime}')
            
            level = 0.0
            if self.batteryVoltage == 'n.p.':
                level = 99.
            else:
                level  = float(self.batteryVoltage)
            if level < GB.BATTERY_WARNING_LEVEL:
                self._cf.param.set_value('ring.effect', '13')
                print (Fore.YELLOW + 'WARNING, sono il drone %s e comincio ad avere la batteria un po\' scarica (%s)' % (self.ID, level))
                if (GB.FILE_LOGGING_ENABLED):  self.LoggerObject.warning("battery under %sv" % GB.BATTERY_WARNING_LEVEL)
                # self.isReadyToFly = False
            if level < GB.BATTERY_DRAINED_LEVEL:
                self._cf.param.set_value('ring.effect', '11')  #alert
                if self.statoDiVolo == 'landed':
                    print ('ciao, sono il drone %s e sono così scarico che non posso più far nulla. (%s)' %  (self.ID, level))
                    self.statoDiVolo  = 'depleted'
                    self.isReadyToFly = False
                else:
                    print (Fore.RED + 'ciao, sono il drone %s e sono così scarico che atterrerei. (%s)' %  (self.ID, level))
                    if (GB.FILE_LOGGING_ENABLED): self.LoggerObject.error("battery under %sV ! I AM GOING DOWN" % GB.BATTERY_DRAINED_LEVEL )
                    self.land(thenGoToSleep=True)
                    self.statoDiVolo = 'landed'
                    self.isFlying = False
                    self.isReadyToFly = False
            # batteryLock.release()
            time.sleep(GB.BATTERY_CHECK_RATE)
        print('battery thread for drone %s stopped'% self.ID)
        # del self.killingPill
        del self.batteryThread
    def check_out_of_boxiness(self):
        if abs(self.x) > (GB.BOX_X + 1.0) or abs(self.y) > (GB.BOX_Y+1.0) or self.z > (GB.BOX_Y + 0.5):
                    print(Fore.RED + 'Landing due trespassing!')
                    self.currentSequence_killingPill.set()
                    self.LoggerObject.info("Landing due trespassing!")
                    self.land(thenGoToSleep=True)
 
    ####################################################################     wake / sleep
 
    def killMeSoftly(self):
        self.land(thenGoToSleep=True)
    def killMeHardly(self):
        self.isFlying = False
        self.goToSleep()
        self.exit()
    def goToSleep(self):
        self.is_connected = False
        self.standBy = True
        self.isFlying = False
        # self.killingPill.set()
        self.currentSequence_killingPill.set()
        time.sleep(0.2)
            # self._cf.close_link()
        self.exit()
        self.statoDiVolo = 'stand by'
    def wakeUp(self):
        def wakeUpProcedure():
            print('mi sveglio')
            self.statoDiVolo = 'waking up'
        
            if not GB.WE_ARE_FAKING_IT:
                self.killingPill.clear()
                self.currentSequence_killingPill.clear()
                self.standBy = False
                PowerSwitch(self.link_uri).stm_power_cycle()
            print('stiamo aspettando 4 secondi')
            time.sleep(6)
            print('aspettati')
            self.connect()
        daje = threading.Thread(target=wakeUpProcedure).start()

    def exit(self):
        print('drogno %s is now doomed, bye kiddo' % self.name)
        self.multiprocessConnection.send('fuck you')
        self.isKilled = True
        self.isReadyToFly = False
        self.killingPill.set()
        print ('waiting for drogno %s\'s feedback to close' % self.ID)
        # self.feedbackProcess.join()
        print ('closing drogno %s\'s radio' % self.ID)
        del GB.drogni[self.ID]
        if (GB.FILE_LOGGING_ENABLED): self.LoggerObject.warning("closing %s"% self.name)
        if not GB.WE_ARE_FAKING_IT:
            self._cf.close_link()
            self._cf.is_connected = False
            
            time.sleep(0.2)
            PowerSwitch(self.link_uri).close()
            time.sleep(0.2)

            PowerSwitch(self.link_uri).stm_power_down()

        