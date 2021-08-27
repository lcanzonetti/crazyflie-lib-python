#rf 2021
import threading
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

BOX_X                 = 1.5
BOX_Y                 = 1.5
BOX_Z                 = 1.9
DEFAULT_HEIGHT        = 0.8
RELATIVE_SPACING      = 0.4
BATTERY_CHECK_RATE    = 1.0
STATUS_PRINT_RATE     = 2.0
RED                   = '0x555500'
GREEN                 = '0x00AA00'
BLUE                  = '0x0000AA'



class Drogno(threading.Thread):
    def __init__(self, ID, link_uri, exitFlag, perhapsWeReFakingIt):
        threading.Thread.__init__(self)
        self.link_uri    = link_uri
        self.ID          = int(ID)
        self.name        = 'Drogno_'+str(ID)
        self.statoDiVolo = 'starting'
        self.durataVolo  = random.randint(1,4)
        self.exitFlag    = exitFlag
        self.WE_ARE_FAKING_IT = perhapsWeReFakingIt
        self.killed      = False
        self.isReadyToFly          = False
        self.isFlying              = False
        self.controlThread         = False
        self.printThread           = False
        self.printRate             = STATUS_PRINT_RATE
        self.currentSequenceThread = False
        self.exitingTimer          = False
        self.idleExitTime          = 10    #seconds
        self.recconnectionAttempts = 0
        self.is_connected          = False
        self.isPositionEstimated   = False
        self.HLCommander           = None
        self.positionHLCommander   = None 
        self.starting_x            = 'np'
        self.starting_y            = 'np'
        self.starting_z            = 'np'
        self.x                     = 0.0
        self.y                     = 0.0 
        self.z                     = 0.0
        self.requested_X            = 0.0
        self.requested_Y            = 0.0
        self.requested_Z            = 0.0
        self.requested_R            = 0
        self.requested_G            = 0
        self.requested_B            = 0
        self.yaw                   = 0.0
        self.batteryVoltage        = 4.2
        self.ringIntensity         = 0.1
        self.goToCount             = 0.0

        self._cf = Crazyflie(rw_cache='./fileVarii/cache')
        # Connect some callbacks from the Crazyflie API
        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)
     
    def run(self):
        print (Fore.LIGHTBLUE_EX + "Starting " + self.name)
        if self.WE_ARE_FAKING_IT:
            time.sleep(1.5)
        else:
            self.printThread   = threading.Thread(target=self.printStatus).start()
            self.batteryThread = threading.Thread(target=self.evaluateBattery)
            self.connect()
     
    def exit(self):
                print('exitFlag is now set for drogno %s, bye kiddo' % self.name)       
                self.exitFlag = 1

    def printStatus(self):
        while not self.exitFlag:
            time.sleep(self.printRate)
            if self.is_connected:
                print (Fore.GREEN  +  f"{self.name}: {self.statoDiVolo} : battery {self.batteryVoltage:0.2f} : pos {self.x:0.2f} {self.y:0.2f} {self.z:0.2f} rotazione: {self.yaw:0.2f} msg/s {self.goToCount/self.printRate}")
                self.goToCount = 0
            else:
                print (Fore.LIGHTBLUE_EX  +  f"{self.name}: {self.statoDiVolo}  msg/s {self.goToCount/self.printRate}")
            # print(f"\nYour Celsius value is {self.x:0.2f} {self.y:0.2f}\n")
                    
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
        self._cf.close_link()
        def mariconnetto():
            if self.recconnectionAttempts == 0:
                print(f'provo a riaprire la connessione con il drogno {self.name}')
                self.recconnectionAttempts+=1
                self._cf.open_link( self.link_uri)

            elif self.recconnectionAttempts >= 1 and self.recconnectionAttempts < 10:
                while self.is_connected == False and self.recconnectionAttempts < 10: 
                    print(f'provo a riaprire la connessione con il drogno {self.name} dopo {self.recconnectionAttempts} tentativi.')
                    self.recconnectionAttempts +=1
                    self._cf.open_link( self.link_uri)
                    print('Aspetto 1 secondo prima di ritentare')
                    time.sleep(1)
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
        print('Waiting for estimator to find position...')

        log_config = LogConfig(name='Kalman Variance', period_in_ms=500)
        log_config.add_variable('kalman.varPX', 'float')
        log_config.add_variable('kalman.varPY', 'float')
        log_config.add_variable('kalman.varPZ', 'float')

        var_y_history = [1000] * 10
        var_x_history = [1000] * 10
        var_z_history = [1000] * 10

        # threshold =5
        threshold = 0.01

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
        time.sleep(0.2)
        self._cf.param.set_value('kalman.resetEstimation', '0')
        time.sleep(0.2)
        # self.wait_for_position_estimator()

    def _connected(self, link_uri):   ##########   where a lot of things happen
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""
        print('Connected to %s' % link_uri)

        # Variable used to keep main loop occupied until disconnect
        self.is_connected = True
        # The definition of the logconfig can be made before connecting
        self._lg_stab = LogConfig(name='Stabilizer', period_in_ms=500)
        self._lg_stab.add_variable('stateEstimate.x', 'float')
        self._lg_stab.add_variable('stateEstimate.y', 'float')
        self._lg_stab.add_variable('stateEstimate.z', 'float')
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
            
            time.sleep(0.3)
            self.reset_estimator()

            self._cf.param.set_value('commander.enHighLevel', '1')
            # self.setRingColor(0,0,0, 0)
            self._cf.param.set_value('ring.effect', '14')
            
            self.HLCommander = self._cf.high_level_commander
            self.positionHLCommander = PositionHlCommander(
                self._cf,
                x=self.x, y=self.y, z=0.0,
                default_velocity=0.5,
                default_height=DEFAULT_HEIGHT,
                controller=PositionHlCommander.CONTROLLER_PID) 
            
            self._lg_stab.start()
            self.batteryThread.start()
            self._cf.param.set_value('ring.fadeTime', 0.25)

            self.isReadyToFly = True
            self.statoDiVolo = 'landed'
            # self.setRingColor(20,1,1, 2)

     
        except KeyError as e:
            print('Could not start log configuration,'
                  '{} not found in TOC'.format(str(e)))
        except AttributeError:
            print('Could not add Stabilizer log config, bad configuration.')
        
    def _stab_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print('Error when logging %s: %s' % (logconf.name, msg))

    def _stab_log_data(self, timestamp, data, logconf):  #riceve il feedback dei sensori e registra i dati
        self.x              = float(data['stateEstimate.x'])
        self.y              = float(data['stateEstimate.y'])
        self.z              = float(data['stateEstimate.z'])
        self.yaw            = float(data['stabilizer.yaw'])
        self.batteryVoltage = float(data['pm.vbat'])

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the specified address)"""
        print('Connessione la drogno %s fallita: %s' % (self.ID, msg))
        self.is_connected = False
        self.statoDiVolo = 'sconnesso'
        # self._cf.close_link()
        # time.sleep(1)
        self.reconnect()

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print('Me son perso %s dice: %s' % (link_uri, msg))
        self.is_connected = False
        self.statoDiVolo = 'sconnesso'
        # self._cf.close_link()
        # time.sleep(1)
        self.reconnect()

    def _disconnected(self, link_uri):
        if self.is_connected == True:
            """Callback when the Crazyflie is disconnected (called in all cases)"""
            print('Deh, son sconnesso da %s' % link_uri)
            self.is_connected = False
            self.statoDiVolo = 'sconnesso'
            # self._cf.close_link()
            # time.sleep(1)
            self.reconnect()

    def takeoff(self, height=DEFAULT_HEIGHT, time=1.5):
        print('like, now')
        if self.WE_ARE_FAKING_IT:
            time.delay(1)
            self.statoDiVolo = 'decollato!'
            self.isFlying  = True
        else:
            print('for real')
            if self.isReadyToFly:
                # self.reset_estimator()
                self.starting_x  = self.x
                self.starting_y  = self.y
                self.statoDiVolo = 'taking off!'
                self.HLCommander.takeoff(DEFAULT_HEIGHT, 2)
                # self.positionHLCommander.take_off()
                self.statoDiVolo = 'hovering'
                self.isFlying    = True
            else:
                print('BUT NOT READY')

    def land(self, speed=0.15, landing_height=0.03):
        def landing_sequence():
            self._cf.high_level_commander.land(0.0, 3.0)
            self.isFlying     = False
            time.sleep(3)
            # self._cf.commander.send_position_setpoint(self.starting_x, self.starting_y, 0.05, 180)
            # time.sleep(0.1)

            # self._cf.commander.send_stop_setpoint()

            self.isReadyToFly = True
            self.statoDiVolo = 'landed'

        if self.WE_ARE_FAKING_IT:
            self.statoDiVolo = 'landing'
            time.sleep(1)
            self.isReadyToFly = True
            self.statoDiVolo = 'landed'
        else:
            if self.isFlying:
                print('%s atterra! ' % self.name)
                self.statoDiVolo = 'landing'
                ld = threading.Thread(target=landing_sequence).start()
                # ld.join()
            else:
                print('%s can\'t land! (not flying)' % self.name)

    def goTo(self,x,y,z, yaw=0, speed=0.1):  #la zeta è in alto!
        self.goToCount += 1

        if self.isFlying:
            clamp(x, -BOX_X, BOX_X)
            clamp(y, -BOX_Y, BOX_Y)
            clamp(z, 0.3   , BOX_Z)
            # print('%s va a %s %s %s' % (self.name,  x,y,z))
            self.statoDiVolo = 'moving'
            self._cf.high_level_commander.go_to(x,y,z, yaw,1)
            self.statoDiVolo = 'hovering'
        else:
            print('perhaps take off?')

    def goLeft(self, quanto=0.3):
        if self.isFlying:
            newX = float(self.x) - float(quanto)
            print('va bene, vado a %s' % newX)
            self._cf.high_level_commander.go_to(-quanto, self.y, self.z, 0, 1, relative=True)

    def goRight(self, quanto=0.3):
        if self.isFlying:
            newX = float(self.x) + float(quanto)
            print('va bene, vado a %s' % newX)
            self._cf.high_level_commander.go_to(quanto, self.y, self.z, 0, 1, relative=True)

    def goForward(self, quanto=0.3):
        if self.isFlying:
            newY = float(self.y) + float(quanto)
            print('va bene, vado a %s' % newY)
            self._cf.high_level_commander.go_to(self.x, newY, self.z, 0, 1)

    def goBack(self, quanto=0.3):
        if self.isFlying:
            newY = float(self.y) - float(quanto)
            print('va bene, vado a %s' % newY)
            self._cf.high_level_commander.go_to(self.x, newY, self.z, 0, 1)

    def goToHome(self, speed=0.5):
        if self.isFlying:                
            self._cf.high_level_commander.go_to(self.starting_x,self.starting_y,1, 0, 1)
        print(Fore.LIGHTCYAN_EX + 'Guys, I\'m %s, and I\'m gonna go home to %s %s' % (self.name, self.starting_x, self.starting_y ) )

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
        if self.statoDiVolo == 'hovering' or self.statoDiVolo == 'finito sequenza' or self.statoDiVolo == 'idle':
            if self.WE_ARE_FAKING_IT:
                self.statoDiVolo = 'sequenza simulata!'
            else:
                self.statoDiVolo = 'sequenza!'
                print ('eseguo la sequenza %s' % sequenceNumber)
                self.sequenzaTest(sequenceNumber)
        else:
            print('not ready!')

    def sequenzaTest(self,sequenceNumber=0,loop=False):
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
            self.setRingColor(255,   0,   0, 1.0, 1.0)
            time.sleep(1)

            self.positionHLCommander.go_to(0.0, 1+RELATIVE_SPACING, 1, 0.2)
            self.setRingColor(255,   0,   0, 1.0, 1.0)

            self.positionHLCommander.go_to(1+RELATIVE_SPACING, 1+RELATIVE_SPACING, 1, 0.2)
            self.setRingColor(  0, 255,  0, 1.0, 1.0)
            
            self.positionHLCommander.go_to(1.0+RELATIVE_SPACING, 0.0+RELATIVE_SPACING, 1, 0.2)
            self.setRingColor(  0,   0, 255, 1.0, 1.0)

            self.positionHLCommander.go_to(0.0+RELATIVE_SPACING, 0.0+RELATIVE_SPACING, 1, 0.2)
            self.setRingColor(255, 255,   0, 1.0, 1.0)
            time.sleep(1)

            self.setRingColor(255, 255,   0, 1.0, 1.0)
            time.sleep(1)
            self.setRingColor(255, 255,   0, 1.0, 1.0)
            time.sleep(1)
            print('fine prima sequenza di test')
            self.statoDiVolo = 'landed'
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
            self.positionHLCommander.land()
            # self._cf.commander.send_stop_setpoint()
            self.statoDiVolo = 'landed'

        
        sequenzeTest = [sequenzaZero, sequenzaUno, sequenzaDue, sequenzaTre, sequenzaQuattro]

        if not self.currentSequenceThread:
            self.currentSequenceThread = threading.Thread(target=sequenzeTest[sequenceNumber])
            self.currentSequenceThread.start()
            print('non ci sono sequenze in esecuzione, parto con la %s' % sequenceNumber)
        else:
           print('la sequenza in esecuzione non può essere fermata. \nMAI')

    def evaluateBattery(self):
        while not self.exitFlag:
            level = self.batteryVoltage 
            if level<3.50:
                print (Fore.YELLOW + 'ciao, sono il drone %s e comincio ad avere la batteria un po\' scarica (%s)' % (self.ID, level))
            if level<3.35:
                if self.statoDiVolo == 'landed':
                    print ('ciao, sono il drone %s e sono così scarico che non posso più far nulla. (%s)' %  (self.ID, level))
                    self.statoDiVolo == 'landed with no battery'
                    # self._cf.high_level_commander.stop()
                    # self._cf.commander.send_stop_setpoint()
                else:
                    print (Fore.RED + 'ciao, sono il drone %s e sono così scarico che atterrerei. (%s)' %  (self.ID, level))
                    self.land()
                    self.statoDiVolo = 'landed'
                    self.isReadyToFly = False
            time.sleep(BATTERY_CHECK_RATE)

    def killMeSoftly(self):
            self.killed = True
            self.land()
            self.exit()
    def killMeHardly(self):
            self.killed = True
            self.setRingColor(0,0,0)
            self._cf.high_level_commander.stop()
            self._cf.commander.send_stop_setpoint()
            self._cf.loc.send_emergency_stop()
            self._cf.close_link()
            self.exit()




def clamp(num, min_value, max_value):
   return max(min(num, max_value), min_value)