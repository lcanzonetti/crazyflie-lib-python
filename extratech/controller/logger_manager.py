

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
        print('tipo')
        print(self.parent_drogno)
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
        self.fast_logging.add_variable('sys.isTumbled',        'uint8_t')



        self.slow_logging.add_variable('kalman.stateX',           'FP16')
        self.slow_logging.add_variable('kalman.stateY',           'FP16')
        self.slow_logging.add_variable('kalman.stateZ',           'FP16')
        self.slow_logging.add_variable('stateEstimate.yaw',       'FP16')
        self.slow_logging.add_variable('sys.isTumbled',        'uint8_t')
        self.slow_logging.add_variable('radio.rssi',           'uint8_t')
        self.slow_logging.add_variable('pm.vbat',                 'FP16')
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
            self.parent_drogno.x                 = float(data['stateEstimateZ.x'])
            self.parent_drogno.y                 = float(data['stateEstimateZ.x'])
            self.parent_drogno.z                 = float(data['stateEstimateZ.x'])
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
        if new_level == -1:
            for ll in self.logging_levels:
                self.logging_levels[ll].stop()
                
        old_level = self.current_logging
        self.current_logging = new_level
        self.logging_levels[old_level].start()
        time.sleep(0.5)
        self.logging_levels[new_level].stop()

    def get_logging_level(self):
        return self.logging_levels[self.current_logging]

    def print_status(self):
    # A good rule of thumb is that one radio can handle at least 500 packets per seconds 
    # in each direction and each log block uses one packet per log.
    # So it should be possible to log at 100Hz a couple of log blocks. 
        if GB.FILE_LOGGING_ENABLED:
            self.LoggerObject.info('Logger started')
            while not self.killingPill.is_set():
                time.sleep(GB.print_rate)
                if not GB.WE_ARE_FAKING_IT:    
                    if self.is_connected:
                        self.LoggerObject.info(f"{self.name}: {self.statoDiVolo}\tbattery: {self.batteryVoltage}\tkalman var: {round(self.kalman_VarX,3)} {round(self.kalman_VarY,3)} {round(self.kalman_VarZ,3)}\t batterySag: {round(self.batterySag,3)}\tlink quality: {self.linkQuality}\tflight time: {self.flyingTime}s\tpos {self.x:0.2f} {self.y:0.2f} {self.z:0.2f}\tyaw: {self.yaw:0.2f}\tmsg/s {round((self.commandsCount/GB.print_rate),1)}")
                        if self.isEngaged:
                            if GB.INITIAL_TEST: print (Fore.LIGHTRED_EX  +  f"{self.name}: {self.statoDiVolo}\t\tbattery {self.batteryVoltage}\tpos {self.x:0.2f} {self.y:0.2f} {self.z:0.2f}\tyaw: {self.yaw:0.2f}\tmsg/s {self.commandsCount/GB.print_rate}\tlink quality: {self.linkQuality}\tkalman var: {round(self.kalman_VarX,3)} {round(self.kalman_VarY,3)} {round(self.kalman_VarZ,3)}\tflight time: {self.flyingTime}s\t batterySag: {self.batterySag}\t motorPass: {self.motorPass}")
                            else: print (Fore.LIGHTRED_EX  +  f"{self.name}: {self.statoDiVolo}\t\tbattery {self.batteryVoltage}\tpos {self.x:0.2f} {self.y:0.2f} {self.z:0.2f}\tyaw: {self.yaw:0.2f}\tmsg/s {self.commandsCount/GB.print_rate}\tlink quality: {self.linkQuality}\tkalman var: {round(self.kalman_VarX,3)} {round(self.kalman_VarY,3)} {round(self.kalman_VarZ,3)}\tflight time: {self.flyingTime}s ")
                        else:
                            print (Fore.GREEN  +  f"{self.name}: {self.statoDiVolo}\t\tbattery {self.batteryVoltage}\tpos {self.x:0.2f} {self.y:0.2f} {self.z:0.2f}\tyaw: {self.yaw:0.2f}\tmsg/s {self.commandsCount/GB.print_rate}\tlink quality: {self.linkQuality}\tkalman var: {round(self.kalman_VarX,3)} {round(self.kalman_VarY,3)} {round(self.kalman_VarZ,3)}\tflight time: {self.flyingTime}s ")
                    else:
                        print (Fore.LIGHTBLUE_EX  +  f"{self.name}: {self.statoDiVolo}")
                else:
                    if self.is_connected:
                        self.LoggerObject.info(f"{self.name}: {self.statoDiVolo}\tbattery: fake\tkalman var: fake\t batterySag: fake\tlink quality: {self.linkQuality}\tflight time: {self.flyingTime}s\tpos: fake somewhere\tyaw: fake\tmsg/s {round((self.commandsCount/GB.print_rate),1)}")
                        if self.isEngaged:
                            print(Fore.LIGHTRED_EX + f"{self.name}: {self.statoDiVolo}\t\tbatteryfake\tpos {self.x:0.2f} {self.y:0.2f} {self.z:0.2f}\tyaw: {self.yaw:0.2f}\tmsg/s {self.commandsCount/GB.print_rate}\tlink quality: {self.linkQuality}\tkalman var: {round(self.kalman_VarX,3)} {round(self.kalman_VarY,3)} {round(self.kalman_VarZ,3)}\tflight time: {self.flyingTime}s ")
                        else:
                            print(Fore.GREEN + f"{self.name}: {self.statoDiVolo}\t\tbattery fake\tpos super fake\tyaw: fake\tflight time: {self.flyingTime}s ")
                    else:
                        print(Fore.LIGHTBLUE_EX + f"{self.name}: {self.statoDiVolo}")

                self.commandsCount = 0

                if not self.scramblingTime == None and self.isFlying:
                    self.flyingTime = int(time.time() - self.scramblingTime)
            print('Log chiuso per %s ' % self.name)

