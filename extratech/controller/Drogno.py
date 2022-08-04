#rf 2022
import time, sys, os
import threading
from   threading import Lock
from datetime import datetime
import multiprocessing
from   multiprocessing.connection import Client
from   colorama             import Fore, Back, Style
from   colorama             import init as coloInit

from main import WE_ARE_FAKING_IT
coloInit(convert=True)

#crazyflie'sm
import logging
from   cflib.crazyflie                            import Crazyflie, commander
# from   cflib.utils                                import uri_helper
from   cflib.crazyflie.log                        import LogConfig
from   cflib.positioning.position_hl_commander    import PositionHlCommander
from   cflib.crazyflie.mem import MemoryElement
from   cflib.crazyflie.mem import Poly4D
from   cflib.utils.power_switch import PowerSwitch
import OSC_feedabcker as feedbacker

BOX_X                 = 2.2
BOX_Y                 = 2.2
BOX_Z                 = 2.2
LIGHTHOUSE_METHOD     = '0'
DEFAULT_HEIGHT        = 0.8
DEFAULT_VELOCITY      = 0.85
DEFAULT_SCRAMBLING_TIME = 2.2
RELATIVE_SPACING      = 0.4
BATTERY_CHECK_RATE    = 0.5
STATUS_PRINT_RATE     = 1.1
LOGGING_FREQUENCY     = 1000
COMMANDS_FREQUENCY    = 0.1
FEEDBACK_SENDING_IP   = '127.0.0.1'
FEEDBACK_SENDING_PORT = 9203
FEEDBACK_ENABLED      = True
CLAMPING              = True
RING_FADE_TIME        = 0.001
BATTERY_TEST          = True

class Drogno(threading.Thread):
    def __init__(self, ID, link_uri, exitFlag, processes_exit_event, perhapsWeReFakingIt, startingPoint, lastRecordPath):
        threading.Thread.__init__(self)
        # self.lastRecordPath  = lastRecordPath
        # self.lastTrajectory  = ''
        # self.TRAJECTORIES    = {}
        # self.currentTrajectoryLenght = 0
        self.link_uri    = link_uri
        self.ID          = int(ID)
        self.name        = 'Drogno_'+str(ID)
        self.statoDiVolo = 'starting'
        # self.durataVolo  = random.randint(1,4)
        self.exitFlag    = exitFlag
        self.WE_ARE_FAKING_IT       = perhapsWeReFakingIt
        self.isKilled               = False
        self.isReadyToFly           = False
        self.isEngaged              = True
        self.isBatterytestPassed    = False
        self.isFlying               = False
        self.controlThread          = False
        self.printThread            = False
        self.printRate              = STATUS_PRINT_RATE
        # self.currentSequenceThread  = False
        self.recconnectionAttempts  = 0
        self.is_connected           = False
        self.standBy                = False
        self.isPositionEstimated    = False
        self.positionHLCommander    = None 
        self.starting_x             = 0.0
        self.starting_y             = 0.0
        self.starting_z             = 0.0
        self.x                      = 0.0
        self.y                      = 0.0 
        self.z                      = 0.0
        self.yaw                    = 0.0
        self.requested_X            = 0.0
        self.requested_Y            = 0.0
        self.requested_Z            = 0.0
        self.requested_R            = 0
        self.requested_G            = 0
        self.requested_B            = 0
        self.ledMem                 = 0
        self.kalman_VarX            = 0
        self.kalman_VarY            = 0
        self.kalman_VarZ            = 0
        self.esteemsCount           = 0
        self.prefStartPoint_X       = startingPoint[0]
        self.prefStartPoint_Y       = startingPoint[1]
        self.batteryVoltage         = 'n.p.'
        self.batterySag             = 0
        self.ringIntensity          = 0.1
        self.commandsCount          = 0.0
        self.multiprocessConnection = None
        self.linkQuality            = 0
        self.isTumbled              = False
        self.commandsFrequency      = COMMANDS_FREQUENCY
        self.connection_time        = None
        self.scramblingTime         = None
        self.flyingTime             = 0
        self.connectionThread       = None
        self.killingPill            = None
        self._cf = Crazyflie(rw_cache='./cache_test')
        # Connect some callbacks from the Crazyflie API
        self._cf.connected.add_callback(self._connected)
        self._cf.fully_connected.add_callback(self._fully_connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)
        # Feedback instance in his own process
        self.feedbacker_receiving_port = 9100 + self.ID
        self.feedbacker_address        = ('127.0.0.1', self.feedbacker_receiving_port)
        self.feedbacker                = feedbacker.Feedbacco(self.ID, processes_exit_event, FEEDBACK_SENDING_IP,FEEDBACK_SENDING_PORT, self.feedbacker_receiving_port  )
        self.feedbackProcess           = multiprocessing.Process(name=self.name+'_feedback',target=self.feedbacker.start).start()
        ################################################## logging
        now = datetime.now() # current date and time
        date_time = now.strftime("%m_%d_%Y__%H_%M_%S")
        logName = "./extratech/controller/drognoLogs/" + self.name + "_" +date_time + ".log"
        os.makedirs(os.path.dirname(logName), exist_ok=True)
        self.LoggerObject = logging.getLogger(self.name)
        self.LoggerObject.setLevel(logging.DEBUG)
        self.file_handler = logging.FileHandler(logName, mode="w", encoding=None, delay=False)
        self.formatter    = logging.Formatter('%(levelname)s: %(asctime)s %(funcName)s(%(lineno)d) -- %(message)s', datefmt = '%d-%m-%Y %H:%M:%S')
        self.file_handler.setFormatter(self.formatter)
        self.LoggerObject.addHandler(self.file_handler)
        self.LoggerObject.info('This is dronelog running on %s' % self.name)

    def run(self):
        print (Fore.LIGHTBLUE_EX + "starting " + self.name)
        # self.TRAJECTORIES [0] = self.lastRecordPath + '/trajectory_' + str(self.ID) + '.txt'
        # self.TRAJECTORIES [7] = figure8Triple
        # self.TRAJECTORIES [8] = figure8
    
        # print ('my trajectories are: %s' % self.TRAJECTORIES [8])
        # with open(trajectory, 'r') as t:
        #     # print(t.readlines())
        #     self.lastTrajectory = t.readlines()
         # Modifying the log file we are using


        if self.WE_ARE_FAKING_IT:
            # print (Fore.LIGHTBLUE_EX + "Faking it = " + str(self.WE_ARE_FAKING_IT ))
            self.connect()
            time.sleep(1.5)
        else:
            # print('We are not faking it this time.')
            connectedToFeedback = False
            if FEEDBACK_ENABLED and not self.exitFlag.is_set():
                time.sleep(0.5)
                while not connectedToFeedback:
                    try:
                        time.sleep(0.1)
                        self.multiprocessConnection = Client(self.feedbacker_address)
                        connectedToFeedback = True
                    except ConnectionRefusedError:
                        print('server del drogno %s feedback non ancora connesso!' % self.I)

            self.printThread   = threading.Thread(target=self.printStatus).start()
            self.connect()
     
    def printStatus(self):
        # printLock = Lock()
        self.LoggerObject.info('Started')
        while not self.exitFlag.is_set():
            time.sleep(self.printRate)

            if self.is_connected:
                self.LoggerObject.info(f"{self.name}: {self.statoDiVolo}\tbattery: {self.batteryVoltage}\tkalman var: {round(self.kalman_VarX,3)} {round(self.kalman_VarY,3)} {round(self.kalman_VarZ,3)}\t batterySag: {round(self.batterySag,3)}\tlink quality: {self.linkQuality}\tflight time: {self.flyingTime}s\tpos {self.x:0.2f} {self.y:0.2f} {self.z:0.2f}\tyaw: {self.yaw:0.2f}\tmsg/s {round((self.commandsCount/self.printRate),1)}")
                if self.isEngaged:
                    if BATTERY_TEST: print (Fore.LIGHTRED_EX  +  f"{self.name}: {self.statoDiVolo}\t\tbattery {self.batteryVoltage}\tpos {self.x:0.2f} {self.y:0.2f} {self.z:0.2f}\tyaw: {self.yaw:0.2f}\tmsg/s {self.commandsCount/self.printRate}\tlink quality: {self.linkQuality}\tkalman var: {round(self.kalman_VarX,3)} {round(self.kalman_VarY,3)} {round(self.kalman_VarZ,3)}\tflight time: {self.flyingTime}s\t batterySag: {self.batterySag}")
                    print (Fore.LIGHTRED_EX  +  f"{self.name}: {self.statoDiVolo}\t\tbattery {self.batteryVoltage}\tpos {self.x:0.2f} {self.y:0.2f} {self.z:0.2f}\tyaw: {self.yaw:0.2f}\tmsg/s {self.commandsCount/self.printRate}\tlink quality: {self.linkQuality}\tkalman var: {round(self.kalman_VarX,3)} {round(self.kalman_VarY,3)} {round(self.kalman_VarZ,3)}\tflight time: {self.flyingTime}s ")
                else:
                    print (Fore.GREEN  +  f"{self.name}: {self.statoDiVolo}\t\tbattery {self.batteryVoltage}\tpos {self.x:0.2f} {self.y:0.2f} {self.z:0.2f}\tyaw: {self.yaw:0.2f}\tmsg/s {self.commandsCount/self.printRate}\tlink quality: {self.linkQuality}\tkalman var: {round(self.kalman_VarX,3)} {round(self.kalman_VarY,3)} {round(self.kalman_VarZ,3)}\tflight time: {self.flyingTime}s ")
            else:
                print (Fore.LIGHTBLUE_EX  +  f"{self.name}: {self.statoDiVolo}")
            self.commandsCount = 0

            if not self.scramblingTime == None and self.isFlying:
                self.flyingTime = int(time.time() - self.scramblingTime)

        print('Log chiuso per %s ' % self.name)
                    
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

    def resetEstimator(self):
        self.x = self.starting_x
        self.y = self.starting_y
        self.z = 0
        self._cf.param.set_value('kalman.resetEstimation', '1')
        time.sleep(0.5)

        # self._cf.param.set_value('kalman.resetEstimation', '0')
        # time.sleep(0.2)
        print(Fore.MAGENTA + 'estimator reset done on ' + self.name)
        # self.wait_for_position_estimator()
    #################################################################### connection
    def connect(self):
        print(self.link_uri)
        if not WE_ARE_FAKING_IT:
            if self.isKilled == False:
                self.killingPill   = threading.Event()
                self.batteryThread = threading.Thread(name=self.name+'_batteryThread',target=self.evaluateBattery)
                print(f'Provo a connettermi al drone { self.ID} all\'indirizzo { self.link_uri}    ')
                def connection():
                    self.statoDiVolo = 'connecting'
                    try:
                        self._cf.open_link(self.link_uri)
                        self.connection_time = time.time()
                        while not self.exitFlag or self.is_connected:
                            print('.')
                    except IndexError:
                        print('capperi')
                    except:
                        print('no radio pal')
                self.connectionThread = threading.Thread(target=connection).start()
        else:
            self.killingPill   = threading.Event()
            self._connected(self.link_uri)
            time.sleep(2)
            self._fully_connected(self.link_uri)           


    def reconnect(self):
        def mariconnetto():
            if self.recconnectionAttempts == 0:
                print(f'provo a riaprire la connessione con il drogno {self.name}')
                self.recconnectionAttempts+=1
                self.statoDiVolo = 'connecting'
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
        tio = threading.Thread(name=self.name+'_reconnectThread',target=mariconnetto)
        tio.start()

    def _connected(self, link_uri):   ##########   where a lot of things happen
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""
        # print('TOC downloaded for %s, it took %s seconds, waiting for parameters.' % (link_uri, (time.time()-self.connection_time)))
        print('TOC scaricata per il %s, in attesa dei parametri.' % (self.name))
        
    def _fully_connected(self, link_uri):
        # print ('\nil crazyflie %s ha scaricato i parametri \n' % link_uri)
        print('Il drone ha scaricato tutto.')
        # The definition of the logconfig can be made before connecting
        self._lg_kalm = LogConfig(name='Stabilizer', period_in_ms=100)
        # The fetch-as argument can be set to FP16 to save space in the log packet
        self._lg_kalm.add_variable('kalman.stateX', 'FP16')
        self._lg_kalm.add_variable('kalman.stateY', 'FP16')
        self._lg_kalm.add_variable('kalman.stateZ', 'FP16')
        self._lg_kalm.add_variable('kalman.varPX',  'FP16')
        self._lg_kalm.add_variable('kalman.varPY',  'FP16')
        self._lg_kalm.add_variable('kalman.varPZ',  'FP16')
        self._lg_kalm.add_variable('sys.isTumbled', 'uint8_t')
        self._lg_kalm.add_variable('radio.rssi',    'uint8_t')
        self._lg_kalm.add_variable('stabilizer.yaw','FP16')
        self._lg_kalm.add_variable('pm.vbat', 'FP16')
        if BATTERY_TEST: self._lg_kalm.add_variable('health.batterySag', 'FP16')
        try:
            if not WE_ARE_FAKING_IT:                    #### Se stiamo facendo finta evitiamo di fare .add_config e ._lg_kalm.start
                self._cf.log.add_config(self._lg_kalm)
            self._lg_kalm.data_received_cb.add_callback(self._stab_log_data)
            self._lg_kalm.error_cb.add_callback(self._stab_log_error)
            if not WE_ARE_FAKING_IT:                    ####
                self._lg_kalm.start()
            self.is_connected = True
            print(Fore.LIGHTGREEN_EX + '%s fully connesso'% (self.name))
        except KeyError as e:
            print('Could not start log configuration,'
                  '{} not found in TOC'.format(str(e)))
        except AttributeError:
          print('Could not add log config, bad configuration.')
        except RuntimeError:
          print('Porco il padre eterno e al su madonnina')

        if not WE_ARE_FAKING_IT:                        #### Se stiamo facendo finta non proviamo a comunicare con un drone che non esite!
            self._cf.param.set_value('commander.enHighLevel', '1')
            if BATTERY_TEST: self._cf.param.set_value('health.startBatTest', '1')
            self._cf.param.set_value('ring.effect', '13')  #solid color? Missing docs?
            self._cf.param.set_value('lighthouse.method', LIGHTHOUSE_METHOD)
            self.ledMem = self._cf.mem.get_mems(MemoryElement.TYPE_DRIVER_LED)
            self.positionHLCommander = PositionHlCommander(
                self._cf,
                x=self.x, y=self.y, z=0.0,
                default_velocity=DEFAULT_VELOCITY,
                default_height=DEFAULT_HEIGHT,
                controller=PositionHlCommander.CONTROLLER_PID) 

            time.sleep(0.3)
            if not self.batteryThread.is_alive():  self.batteryThread.start()
            self._cf.param.set_value('ring.fadeTime', RING_FADE_TIME)
            time.sleep(1.0)
            self.resetEstimator()

        self.statoDiVolo = 'landed'
        time.sleep(2)
        if WE_ARE_FAKING_IT:
            self.isReadyToFly = self.evaluateFlyness()

    def _stab_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print('Error when logging %s: %s' % (logconf.name, msg))

    def _stab_log_data(self, timestamp, data, logconf):  #riceve il feedback dei sensori e registra i dati - gira il feedback indietro via osc

        print('stab loggo chiamato')
        self.x                 = float(data['kalman.stateX'])
        self.y                 = float(data['kalman.stateY'])
        self.z                 = float(data['kalman.stateZ'])
        self.yaw               = float(data['stabilizer.yaw'])
        self.linkQuality       = data['radio.rssi']
        self.batteryVoltage    = str(round(float(data['pm.vbat']),2))
        self.batterySag        = float(data['health.batterySag'])
        self.kalman_VarX       = float(data['kalman.varPX'])
        self.kalman_VarY       = float(data['kalman.varPY'])
        self.kalman_VarZ       = float(data['kalman.varPZ'])
        self.isTumbled         = bool (data['sys.isTumbled'])
        if self.isTumbled: self.goToSleep()
        if self.isFlying:
            if abs(self.x) > (BOX_X + 1.0) or abs(self.y) > (BOX_Y+1.0) or self.z > (BOX_Y + 0.5):
                print(Fore.RED + 'Landing due trespassing!')
                self.LoggerObject.info("Landing due trespassing!")
                self.land(thenGoToSleep=True)
        
        self.isReadyToFly      = self.evaluateFlyness()
        

        try:
            if FEEDBACK_ENABLED and not self.isKilled and not self.exitFlag.is_set():
                self.multiprocessConnection.send([self.ID, self.x, self.y, self.z, self.batteryVoltage, self.yaw])
            # print('carlo')
        except ConnectionRefusedError:
            print('oooo')
       
    def evaluateFlyness(self):
        if not WE_ARE_FAKING_IT:
            if self.is_connected and not self.standBy:
                if  abs(self.x) > BOX_X or abs(self.y) > BOX_Y or self.z > BOX_Y or self.isTumbled:
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
                else:
                    self._cf.param.set_value('ring.effect', '13')  #solid color? Missing docs?
                    self.statoDiVolo = 'ready'
                    return True
            else:
                # print ('nope nope nope!')
                pass
        else:
            self.statoDiVolo = 'ready'
            return True


    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the specified address)"""
        print('Connessione la drogno %s fallita: %s' % (self.ID, msg))
        self.is_connected = False
        self.isReadyToFly = False
        self.statoDiVolo = 'sconnesso'
        # self.reconnect()

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print('Me son perso %s dice: %s' % (link_uri, msg))
        self.is_connected = False
        self.statoDiVolo = 'sconnesso'
        self.isReadyToFly = False
        # if not self.statoDiVolo == 'connecting':  self.reconnect()

    def _disconnected(self, link_uri):
            """Callback when the Crazyflie is disconnected (called in all cases)"""
            print('Deh, son sconnesso da %s' % link_uri)
            self.is_connected = False
            self.statoDiVolo  = 'sconnesso'
            self.isReadyToFly = False
            # if not self.standBy and not self.isKilled and not self.statoDiVolo == 'connecting':  self.reconnect()
 
    #################################################################### movement

    def takeOff(self, height=DEFAULT_HEIGHT, scramblingTime = DEFAULT_SCRAMBLING_TIME):
        def scramblingsequence():
            self.starting_x  = self.x
            self.starting_y  = self.y
            self.statoDiVolo = 'scrambling!'
            self._cf.high_level_commander.takeoff(DEFAULT_HEIGHT,scramblingTime)
            self.scramblingTime = time.time()
            self.isFlying    = True
            self.statoDiVolo = 'hovering'

        def fake_scramblingsequence():
            self.starting_x  = self.x
            self.starting_y  = self.y
            self.statoDiVolo = 'scrambling!'
            self.scramblingTime = time.time()
            self.isFlying    = True
            self.statoDiVolo = 'hovering'

        if not self.WE_ARE_FAKING_IT:
            print('for real')
            # self.resetEstimator()
            if self.isReadyToFly:
                scremblingThread = threading.Thread(target=scramblingsequence, name=self.name+'_scramblingThread').start()
            else:
                print('NOT READY TO SCRAMBLE!')
        else:
            scremblingThread = threading.Thread(target=fake_scramblingsequence, name=self.name+'_scramblingThread').start()

    def land(self, speed=2.5, landing_height=0.05,thenGoToSleep=False):
        def landing_sequence():
            self._cf.high_level_commander.land(landing_height, speed)
            time.sleep(3)
            self.isFlying     = False
            self.statoDiVolo = 'landed'
            if (thenGoToSleep): self.goToSleep()
            self.isReadyToFly = self.evaluateFlyness()
        
        def fake_landing_sequence():
            time.sleep(speed)
            self.isFlying     = False
            self.statoDiVolo = 'landed'
            if (thenGoToSleep): self.goToSleep()
            self.isReadyToFly = self.evaluateFlyness()

        if not self.WE_ARE_FAKING_IT:
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
                # ld.join()
            
    def goTo(self,x,y,z, yaw=0, duration=0.5):  #la zeta è in alto!
        self.commandsCount += 1
        duration = self.commandsFrequency*3
        if self.isFlying:
            if CLAMPING:
                clamp(x, -BOX_X, BOX_X)
                clamp(y, -BOX_Y, BOX_Y)
                clamp(z, 0.20   , BOX_Z)
            # print('%s va a %s %s %s girato a %s' % (self.name,  x,y,z, yaw))
            self.statoDiVolo = 'moving'
            self._cf.high_level_commander.go_to(x,y,z, yaw,duration)
            self.statoDiVolo = 'hovering'
        # else:
            # print('perhaps take off?')

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
            self._cf.high_level_commander.go_to(self.starting_x,self.starting_y,1.4, 0, 2, False)
        print(Fore.LIGHTCYAN_EX + 'Guys, I\'m %s, and I\'m gonna get a fresh start to %s %s' % (self.name, self.starting_x, self.starting_y ) )

    def setRingColor(self, vr, vg, vb, speed=0.25):
        self.commandsCount += 1

        # vr *= self.ringIntensity
        # vg *= self.ringIntensity
        # vb *= self.ringIntensity

        # color = '0x'
        # color += str ( hex ( int(r) ) ) [2:].zfill(2)
        # color += str ( hex ( int(g) ) ) [2:].zfill(2)
        # color = str ( hex ( int(b) ) ) [2:].zfill(2)
        # self._cf.param.set_value('ring.fadeColor', color)
        # print ('vado al colore %s' % (color))
        
        vr = int(vr * self.ringIntensity)
        vg = int(vg * self.ringIntensity)
        vb = int(vb * self.ringIntensity)

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

        # print ('vado al colore %s' % (vr, vg, vb))

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
            self.positionHLCommander.go_to(self.starting_x, self.starting_y, 1.2, 0.2)
            self.alternativeSetRingColor([255,0,0])
            self.positionHLCommander.go_to(self.starting_x, -self.starting_y, 1.2, 0.2)
            self.alternativeSetRingColor([255,255,0])
            self.positionHLCommander.go_to(self.starting_x, -self.starting_y, 1.2, 0.2)
            self.alternativeSetRingColor([255,255,255])

            self.positionHLCommander.go_to(self.starting_x, self.starting_y, 1.2, 0.2)
            
            print('Drogno: %s. Fine ciclo decollo/atterraggio di test' % self.ID)
            self.statoDiVolo = 'landed'
            if loop:
                self.sequenzaTest(sequenceNumber,loop)
            else:
                print(self._cf.state)
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
        contatore = 0
        def sequenzaQuattro():
            print('Drogno: %s. Inizio test 4' % self.ID)
            self.setRingColor(80,   80,   80)

            self._cf.high_level_commander.go_to(0.5, 0.5, 1, 0, 1)
            time.sleep(1)
            self._cf.high_level_commander.go_to(0.5, -0.5, 1, 0, 1)
            time.sleep(1)
            self._cf.high_level_commander.go_to(-0.5, -0.5, 1, 0, 1)
            time.sleep(1)
            self._cf.high_level_commander.go_to(0.5, -0.5, 1, 0, 1)
            time.sleep(1)
            self._cf.high_level_commander.go_to(0.5, 0.5, 1, 0, 1)
            time.sleep(1)
            self._cf.high_level_commander.go_to(0.0, 0.0, 1, 0, 1)
            # self._cf.commander.set_client_xmode()
            time.sleep(1)
            if contatore < 5: sequenzaQuattro()

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
        # print (Fore.LIGHTYELLOW_EX + 'Exiting class: %s\t Being killed:%s\tConnected: %s ' % (self.exitFlag.is_set(), self.killingPill.is_set(), self.is_connected))
        # batteryLock = Lock()
        while not self.killingPill.is_set() and not self.exitFlag.is_set() and self.is_connected:
            level = 0.0
            # batteryLock.acquire()
            if self.batteryVoltage == 'n.p.':
                level = 99.
            else:
                level  = float(self.batteryVoltage)
            if level<3.50:
                self._cf.param.set_value('ring.effect', '13')
                print (Fore.YELLOW + 'WARNING, sono il drone %s e comincio ad avere la batteria un po\' scarica (%s)' % (self.ID, level))
                self.LoggerObject.warning("battery under 3.50v")

                # self.isReadyToFly = False
            if level<3.33:
                self._cf.param.set_value('ring.effect', '11')  #alert
                if self.statoDiVolo == 'landed':
                    print ('ciao, sono il drone %s e sono così scarico che non posso più far nulla. (%s)' %  (self.ID, level))
                    self.statoDiVolo == 'depleted'
                    self.isReadyToFly = False
                else:
                    print (Fore.RED + 'ciao, sono il drone %s e sono così scarico che atterrerei. (%s)' %  (self.ID, level))
                    self.LoggerObject.error("battery under 3.33v ! GOING DOWN")
                    self.land(thenGoToSleep=True)
                    self.statoDiVolo = 'landed'
                    self.isFlying = False
                    self.isReadyToFly = False
            # batteryLock.release()
            time.sleep(BATTERY_CHECK_RATE)
        print('battery thread for drone %s stopped'% self.ID)
        del self.killingPill
        del self.batteryThread
        
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
        self.killingPill.set()
        time.sleep(0.2)
        self._cf.close_link()
        PowerSwitch(self.link_uri).stm_power_down()
        self.statoDiVolo = 'stand by'

    def wakeUp(self):
        def wakeUpProcedure():
            self.statoDiVolo = 'waking up'
            PowerSwitch(self.link_uri).stm_power_up()
            time.sleep(3)
            self.standBy = False
            self.connect()
        daje = threading.Thread(target=wakeUpProcedure).start()

    def exit(self):
        print('exitFlag is now set for drogno %s, bye kiddo' % self.name)
        self.multiprocessConnection.send('fuck you')
        print ('waiting for drogno %s\'s feedback to close' % self.ID)
        # self.feedbackProcess.join()
        print ('closing drogno %s\'s radio' % self.ID)
        self.LoggerObject.warning("closing %s"% self.name)

        self.isKilled = True
        self._cf.close_link()
        self.isReadyToFly = False
        self.exitFlag.set()

    def sequenzaDiVoloSimulata(self):     
        def volo():
            print('il drone %s vola! e volerà per %s secondi' % (self.ID, self.durataVolo))
            time.sleep(self.durataVolo)
            self.statoDiVolo = 'hovering'

        if not self.currentSequenceThread:
            self.currentSequenceThread = threading.Thread(target=volo)
            self.currentSequenceThread.start()
            print('start!')

def clamp(num, min_value, max_value):
   return max(min(num, max_value), min_value)

def IDFromURI(uri) -> int:
    # Get the address part of the uri
    address = uri.rsplit('/', 1)[-1]
    try:
        return int(address, 16) - 996028180448
    except ValueError:
        print('address is not hexadecimal! (%s)' % address, file=sys.stderr)
        return None
    
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