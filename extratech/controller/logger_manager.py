

import time
import GLOBALS as GB

from   cflib.crazyflie.log                        import LogConfig
from   colorama             import Fore, Back, Style
from   colorama             import init as coloInit
coloInit(convert=True)

"""
Three logging levels:
0: starting
1: fast 
2: slow
"""

class Logger_manager():
    def __init__(self, parent_drogno, cf, ID):
        self.ID = ID
        self.cf = cf
        self.parent_drogno = parent_drogno
        
        self.starting_logging = LogConfig(name='start_log', period_in_ms=200)
        self.fast_logging     = LogConfig(name='fast_log',  period_in_ms=100)
        self.slow_logging     = LogConfig(name='slow_log',  period_in_ms=1000)
        
        self.logging_levels   = \
                                {
                                    0: self.starting_logging,
                                    1: self.fast_logging,
                                    2: self.slow_logging
                                }
       
        self.current_logging  = 0 ## starting
        self.starting_logging.add_variable('kalman.stateX',       'FP16')
        self.starting_logging.add_variable('kalman.stateY',       'FP16')
        self.starting_logging.add_variable('kalman.stateZ',       'FP16')
        self.starting_logging.add_variable('stabilizer.yaw',      'FP16')
        self.starting_logging.add_variable('pm.chargeCurrent',    'FP16')
        self.starting_logging.add_variable('pm.state',         'uint8_t')
        self.starting_logging.add_variable('pm.batteryLevel',  'uint8_t')
        self.starting_logging.add_variable('kalman.varPX',        'FP16')
        self.starting_logging.add_variable('kalman.varPY',        'FP16')
        self.starting_logging.add_variable('kalman.varPZ',        'FP16')
        self.starting_logging.add_variable('sys.isTumbled',    'uint8_t')
        self.starting_logging.add_variable('radio.rssi',       'uint8_t')
        self.starting_logging.add_variable('pm.vbat',             'FP16')
        if GB.INITIAL_TEST:
            self.starting_logging.add_variable('health.batterySag',   'FP16')
            self.starting_logging.add_variable('health.motorPass',    'FP16')


        self.fast_logging.add_variable('stateEstimateZ.x',        'FP16')
        self.fast_logging.add_variable('stateEstimateZ.y',        'FP16')
        self.fast_logging.add_variable('stateEstimateZ.z',        'FP16')
        self.fast_logging.add_variable('stateEstimate.yaw',       'FP16')
        self.fast_logging.add_variable('radio.rssi',           'uint8_t')
        self.fast_logging.add_variable('pm.vbat',                 'FP16')
        self.fast_logging.add_variable('pm.state',             'uint8_t')
        self.fast_logging.add_variable('sys.isTumbled',        'uint8_t')



        self.slow_logging.add_variable('kalman.stateX',           'FP16')
        self.slow_logging.add_variable('kalman.stateY',           'FP16')
        self.slow_logging.add_variable('kalman.stateZ',           'FP16')
        self.slow_logging.add_variable('stateEstimate.yaw',       'FP16')
        self.slow_logging.add_variable('sys.isTumbled',        'uint8_t')
        self.slow_logging.add_variable('radio.rssi',           'uint8_t')
        self.slow_logging.add_variable('pm.vbat',                 'FP16')
        self.slow_logging.add_variable('pm.state',             'uint8_t')
        self.starting_logging.add_variable('sys.isTumbled',    'uint8_t')

    ## aggiunge il log al crazyflie quando  è collegato e innesca il controllo
    def add_log_configurations(self):
        print('aggungo le configurazioni di logging del drone %s ' % self.ID)
        if GB.WE_ARE_FAKING_IT:     #### Se stiamo facendo finta evitiamo di fare .add_config e ._lg_kalm.start
                return 
        try:
            self.cf.log.add_config(self.starting_logging)
            self.starting_logging.data_received_cb.add_callback(self._logging_data)
            self.starting_logging.error_cb.add_callback(self._logging_error)

            self.cf.log.add_config(self.fast_logging)
            self.fast_logging.data_received_cb.add_callback(self._logging_data)
            self.fast_logging.error_cb.add_callback(self._logging_error)

            self.cf.log.add_config(self.slow_logging)
            self.slow_logging.data_received_cb.add_callback(self._logging_data)
            self.slow_logging.error_cb.add_callback(self._logging_error)

        except KeyError as e:
            print('Could not start log configuration {} not found in TOC'.format(str(e)))
        except AttributeError as ae:
            print('Could not add log config for drone %s, bad configuration: %s' % (self.ID, ae))
        except RuntimeError:
            print('Porco il padre eterno e al su madonnina')

    #riceve il feedback dei sensori e registra i dati - gira il feedback indietro via OSC a un sottoprocesso
    def _logging_data(self, timestamp, data, logconf):
        if logconf == self.starting_logging:
            self.parent_drogno.x                 = float(data['kalman.stateX'])
            self.parent_drogno.y                 = float(data['kalman.stateY'])
            self.parent_drogno.z                 = float(data['kalman.stateZ'])
            self.parent_drogno.yaw               = float(data['stabilizer.yaw'])
            if GB.INITIAL_TEST:
                self.parent_drogno.batterySag        = float(data['health.batterySag'])
                self.parent_drogno.motorPass         = float(data['health.motorPass'])
            self.parent_drogno.kalman_VarX       = float(data['kalman.varPX'])
            self.parent_drogno.kalman_VarY       = float(data['kalman.varPY'])
            self.parent_drogno.kalman_VarZ       = float(data['kalman.varPZ'])

            # print('charge_current: %s' % data['pm.chargeCurrent'])
            # print('battery_level:  %s' % data['pm.batteryLevel'])
            # print('pm state:       %s' % data['pm.state'])
 
        elif logconf == self.fast_logging:
            self.parent_drogno.x                 = float(data['stateEstimateZ.x'])/1000
            self.parent_drogno.y                 = float(data['stateEstimateZ.x'])/1000
            self.parent_drogno.z                 = float(data['stateEstimateZ.x'])/1000
            self.parent_drogno.yaw               = float(data['stateEstimate.yaw'])
           
        else:
            self.parent_drogno.x                 = float(data['kalman.stateX'])
            self.parent_drogno.y                 = float(data['kalman.stateY'])
            self.parent_drogno.z                 = float(data['kalman.stateZ'])
            self.parent_drogno.yaw               = float(data['stabilizer.yaw'])

        self.parent_drogno.batteryVoltage    = str(round(float(data['pm.vbat']),2))
        self.parent_drogno.linkQuality       = data['radio.rssi']
        self.parent_drogno.isTumbled         = bool (data['sys.isTumbled'])
        self.parent_drogno.batteryStatus     = int(data['pm.state'])


        # immediately use data to start some checks
        if self.parent_drogno.isTumbled: self.parent_drogno.goToSleep()
        if self.parent_drogno.isFlying:  self.parent_drogno.check_out_of_boxiness()
        self.parent_drogno.isReadyToFly      = self.parent_drogno.evaluateFlyness()
        # forward data to subprocess sending OSC
        try:
            if GB.FEEDBACK_ENABLED and not self.parent_drogno.isKilled and not GB.eventi.get_thread_exit_event().is_set():
                self.parent_drogno.multiprocessConnection.send([self.parent_drogno.ID, self.parent_drogno.x, self.parent_drogno.y, self.parent_drogno.z, self.parent_drogno.batteryVoltage, self.parent_drogno.yaw])
            # print('carlo')
        except ConnectionRefusedError:
            print('Noooo! Non le riesco a dire a nessuno le cose di ' + self.parent_drogno.name)

    def _logging_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print('Error when logging %s for CF %s: %s' % (logconf.name, self.ID, msg))

    def set_logging_level(self, new_level):
        old_level = self.current_logging

        if new_level == -1:
            for ll in self.logging_levels:
                self.logging_levels[ll].stop()
                print('it happens I\'ve just stopped every logging level ')
                return
        elif new_level == old_level:
            self.logging_levels[new_level].start()
            return
        else:
            self.current_logging = new_level
            self.logging_levels[old_level].stop()
            time.sleep(0.5)
            self.logging_levels[new_level].start()
            print('it happens I\'ve just stopped logging level %s to go for logging level %s instead, how fancy.' % (old_level, new_level))

    def get_logging_level(self):
        return self.logging_levels[self.current_logging]

    def print_status(self):
    # A good rule of thumb is that one radio can handle at least 500 packets per seconds 
    # in each direction and each log block uses one packet per log.
    # So it should be possible to log at 100Hz a couple of log blocks. 
        if GB.WE_ARE_FAKING_IT and GB.PRINTING_ENABLED:
            print (Fore.LIGHTBLUE_EX  +  f"{self.parent_drogno.name}: {self.parent_drogno.statoDiVolo}")
            return
        
        if GB.PRINTING_ENABLED:
            while not self.parent_drogno.killingPill.is_set():
                time.sleep(GB.print_rate)
                if self.parent_drogno.is_connected and self.parent_drogno.isEngaged:
                    if self.current_logging == 0:
                        print (Fore.GREEN  +  f"{self.parent_drogno.name}: {self.parent_drogno.statoDiVolo}\t\tbattery {self.parent_drogno.batteryVoltage}\tpos {self.parent_drogno.x:0.2f} {self.parent_drogno.y:0.2f} {self.parent_drogno.z:0.2f}\tyaw: {self.parent_drogno.yaw:0.2f}\tlink quality: {self.parent_drogno.linkQuality}\tkalman var: {round(self.parent_drogno.kalman_VarX,3)} {round(self.parent_drogno.kalman_VarY,3)} {round(self.parent_drogno.kalman_VarZ,3)}")
                    elif self.current_logging == 1 or self.current_logging == 2:
                        print (Fore.YELLOW  +  f"{self.parent_drogno.name}: {self.parent_drogno.statoDiVolo}\t\tbattery {self.parent_drogno.batteryVoltage}\tpos {self.parent_drogno.x:0.2f} {self.parent_drogno.y:0.2f} {self.parent_drogno.z:0.2f}\tyaw: {self.parent_drogno.yaw:0.2f}\tlink quality: {self.parent_drogno.linkQuality}\tmsg/s {self.parent_drogno.commandsCount/GB.print_rate}\tflight time: {self.parent_drogno.flyingTime}")
                    # print (Fore.GREEN  +  f"battery state: {self.parent_drogno.batteryStatus}")
                    if GB.INITIAL_TEST:   print(f'battery SAG: {self.parent_drogno.batterySag}\tisBatteryTestPassed:{self.parent_drogno.isBatteryTestPassed}\tmotor_pass:{self.parent_drogno.motorPass}')
                else:
                    print (Fore.LIGHTBLUE_EX  +  f"{self.parent_drogno.name}: {self.parent_drogno.statoDiVolo}")
                    
    def log_status(self):
        if GB.FILE_LOGGING_ENABLED:
            self.parent_drogno.LoggerObject.info('Logger started')
            while not self.parent_drogno.killingPill.is_set():
                time.sleep(GB.print_rate)
                if not GB.WE_ARE_FAKING_IT and self.parent_drogno.is_connected:
                    self.parent_drogno.LoggerObject.info(f"{self.parent_drogno.name}: {self.parent_drogno.statoDiVolo}\tbattery: {self.parent_drogno.batteryVoltage}\
                    \tkalman var: {round(self.parent_drogno.kalman_VarX,3)} {round(self.parent_drogno.kalman_VarY,3)} {round(self.parent_drogno.kalman_VarZ,3)}\
                    \tbatterySag: {round(self.parent_drogno.batterySag,3)}\tlink quality: {self.parent_drogno.linkQuality}\tflight time: {self.parent_drogno.flyingTime}s\
                    \tpos {self.parent_drogno.x:0.2f} {self.parent_drogno.y:0.2f} {self.parent_drogno.z:0.2f}\tyaw: {self.parent_drogno.yaw:0.2f}\tmsg/s {round((self.parent_drogno.commandsCount/GB.print_rate),1)}")
                    self.parent_drogno.commandsCount = 0
            print('Log chiuso per %s ' % self.parent_drogno.name)


