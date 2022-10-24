

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
    def __init__(self, cf, ID):
        self.ID = ID
        self.cf = cf
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
        self.starting_logging.add_variable('pm.chargeCurrent',   'FP16')
        self.starting_logging.add_variable('pm.state',         'uint8_t')
        self.starting_logging.add_variable('pm.batteryLevel',  'uint8_t')
        self.starting_logging.add_variable('kalman.varPX',        'FP16')
        self.starting_logging.add_variable('kalman.varPY',        'FP16')
        self.starting_logging.add_variable('kalman.varPZ',        'FP16')

        self.starting_logging.add_variable('radio.rssi',       'uint8_t')
        self.starting_logging.add_variable('pm.vbat',             'FP16')
        if GB.INITIAL_TEST:
            self.starting_logging.add_variable('health.batterySag',   'FP16')
            self.starting_logging.add_variable('health.motorPass',    'FP16')


        self.fast_logging.add_variable('stateEstimateZ.x',        'FP16')
        self.fast_logging.add_variable('stateEstimateZ.y',        'FP16')
        self.fast_logging.add_variable('stateEstimateZ.z',        'FP16')
        self.fast_logging.add_variable('stateEstimate.yaw',      'FP16')

        self.fast_logging.add_variable('radio.rssi',           'uint8_t')
        self.fast_logging.add_variable('pm.vbat',                 'FP16')


        self.slow_logging.add_variable('kalman.stateX',           'FP16')
        self.slow_logging.add_variable('kalman.stateY',           'FP16')
        self.slow_logging.add_variable('kalman.stateZ',           'FP16')
        self.fast_logging.add_variable('stateEstimate.yaw',      'FP16')

        self.slow_logging.add_variable('radio.rssi',           'uint8_t')
        self.slow_logging.add_variable('pm.vbat',                 'FP16')


    ## aggiunge il log al crazyflie quando  è collegato e innesca il controllo
    def add_log_configurations(self):
        print('aggungo le configurazioni di logging del drone %s ' % self.ID)
        if GB.WE_ARE_FAKING_IT:     #### Se stiamo facendo finta evitiamo di fare .add_config e ._lg_kalm.start
                return 
        try:
            self.cf.log.add_config(self.starting_logging)
            self.cf.starting_logging.data_received_cb.add_callback(self._logging_data)
            self.cf.starting_logging.error_cb.add_callback(self._logging_error)

            self.cf.log.add_config(self.fast_logging)
            self.cf.fast_logging.data_received_cb.add_callback(self._logging_data)
            self.cf.fast_logging.error_cb.add_callback(self._logging_error)

            self.cf.log.add_config(self.slow_logging)
            self.cf.slow_logging.data_received_cb.add_callback(self._logging_data)
            self.cf.slow_logging.error_cb.add_callback(self._logging_error)

        except KeyError as e:
            print('Could not start log configuration {} not found in TOC'.format(str(e)))
        except AttributeError:
            print('Could not add log config, bad configuration.')
        except RuntimeError:
            print('Porco il padre eterno e al su madonnina')

    #riceve il feedback dei sensori e registra i dati - gira il feedback indietro via OSC a un sottoprocesso
    def _logging_data(self, timestamp, data, logconf):
        if logconf == self.starting_logging:
            self.cf.x                 = float(data['kalman.stateX'])
            self.cf.y                 = float(data['kalman.stateY'])
            self.cf.z                 = float(data['kalman.stateZ'])
            self.cf.yaw               = float(data['stabilizer.yaw'])
            if GB.INITIAL_TEST:
                self.cf.batterySag        = float(data['health.batterySag'])
                self.cf.motorPass         = float(data['health.motorPass'])
            self.cf.kalman_VarX       = float(data['kalman.varPX'])
            self.cf.kalman_VarY       = float(data['kalman.varPY'])
            self.cf.kalman_VarZ       = float(data['kalman.varPZ'])
        elif logconf == self.fast_logging:
            self.cf.x                 = float(data['stateEstimateZ.x'])
            self.cf.y                 = float(data['stateEstimateZ.x'])
            self.cf.z                 = float(data['stateEstimateZ.x'])
            self.cf.yaw               = float(data['stateEstimate.yaw'])
           
        else:
            self.cf.x                 = float(data['kalman.stateX'])
            self.cf.y                 = float(data['kalman.stateY'])
            self.cf.z                 = float(data['kalman.stateZ'])
            self.cf.yaw               = float(data['stabilizer.yaw'])

        self.cf.batteryVoltage    = str(round(float(data['pm.vbat']),2))
        self.cf.linkQuality       = data['radio.rssi']
        self.cf.isTumbled         = bool (data['sys.isTumbled'])
        # immediately use data to start some checks
        if self.cf.isTumbled: self.cf.goToSleep()
        if self.cf.isFlying:  self.cf.cf.check_out_of_boxiness()
        self.cf.isReadyToFly      = self.cf.evaluateFlyness()
        # forward data to subprocess sending OSC
        try:
            if GB.FEEDBACK_ENABLED and not self.cf.isKilled and not GB.eventi.get_thread_exit_event().is_set():
                self.cf.multiprocessConnection.send([self.cf.ID, self.cf.x, self.cf.y, self.cf.z, self.cf.batteryVoltage, self.cf.yaw])
            # print('carlo')
        except ConnectionRefusedError:
            print('Noooo! Non le riesco a dire a nessuno le cose di ' + self.cf.name)

    def _logging_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print('Error when logging %s for CF %s: %s' % (logconf.name, self.ID, msg))


    def set_logging_level(self, new_level):
        old_level = self.current_logging
        self.current_logging = new_level
        self.logging_levels[old_level].start()
        time.sleep(0.5)
        self.logging_levels[new_level].stop()

    def get_logging_level(self):
        return self.logging_levels[self.current_logging]

