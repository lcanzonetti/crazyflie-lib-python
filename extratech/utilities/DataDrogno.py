import threading, time, sys

import numpy as np

from   cflib.crazyflie                            import Crazyflie
from   cflib.crazyflie.syncCrazyflie              import SyncCrazyflie
from   cflib.crazyflie.mem                        import MemoryElement
from   cflib.crazyflie.mem                        import Poly4D
from   cflib.utils                                import uri_helper
import cflib.crtp
from   cflib.crazyflie.log                        import LogConfig


class dataDrone(threading.Thread):
    def __init__(self, ID, link_uri):
        threading.Thread.__init__(self)
        self.ID                     = int(ID)
        self.link_uri               = link_uri
        self.name                   = 'dataDrone '+str(ID)
        self.test_tracker           = [0, 0] # val 0 = props; val 1 = battery
        self.is_testing_over        = False
        self.propeller_test_result  = [0,0,0,0]
        self.battery_test_started   = False
        self.propeller_test_passed  = False
        self.battery_test_passed    = False
        self.battery_sag            = 0.0
        self.battery_voltage        = 0.0
        self.RSSI                   = 0
        self.firmware_revision0     = 0
        self.firmware_revision1     = 0
        self.channel                = None
        self.connection_time        = None
        self.motorTestCount         = None
        self._cf                    = Crazyflie(rw_cache='./extratech/utilities/cache_drogno_%s' %(self.ID))
        self._cf.connected.add_callback(self._connected)
        # self._cf.param.all_updated.add_callback(self._all_params_there)
        self._cf.fully_connected.add_callback(self._fully_connected)

    def test_checker(self):
        while not self.is_testing_over:
            if not (all ( x != 0 for x in self.test_tracker)):
                time.sleep(1)
                pass
            else:
                self.is_testing_over = True
                print ("test finiti per CF %s " % self.name)
                self.close_link()
                
        
    def IDFromURI(self, uri) -> int:
    # Get the address part of the uri
        address = uri.rsplit('/', 1)[-1]
        try:
            # print(int(address, 16) - 996028180448)
            return int(address, 16) - 996028180448
        except ValueError:
            print('address is not hexadecimal! (%s)' % address, file=sys.stderr)
            return None
    
    ### _test propellers           prendono istanza da lista drone, fa il check, scrive il risultato 

    def battery_test(self):
        time.sleep(1.5)
        print('comincio il battery test per %s ' % self.name)
        self._cf.param.set_value('health.startBatTest', '1')

       

    def start_test(self):
        log_conf = LogConfig(name='MotorPass', period_in_ms = 200)
        log_conf.data_received_cb.add_callback(self._crazyflie_logData_receiver)
        log_conf.add_variable('health.motorPass', 'uint8_t')
        log_conf.add_variable('health.motorTestCount', 'uint16_t')
        log_conf.add_variable('pm.vbat', 'FP16')
        log_conf.add_variable('radio.rssi',    'uint8_t')
        log_conf.add_variable('health.batterySag', 'FP16')

        time.sleep(2)
        self._cf.log.add_config(log_conf)
        log_conf.start()
        
        print("il drone %s inizia il Propeller Test... " % self.name)
        self._cf.param.set_value('health.startPropTest', '1')
        
        self._cf.param.set_value('ring.effect', '7')
        self._cf.param.set_value('ring.solidBlue', '255')
        self._cf.param.set_value('ring.solidGreen', '0')
        self._cf.param.set_value('ring.solidRed', '0')

    def _connected(self, link_uri):   
        self._cf.is_connected = True
        print("Mi sono connesso al drone %s all'indirizzo %s" %(self.ID, self.link_uri))
        print('TOC scaricata per il %s, in attesa dei parametri.' % (self.name))

    def _fully_connected(self, link_uri):
        # self.connectToEverything()
        checker           = threading.Thread(target=self.test_checker).start()
        start_test_thread = threading.Thread(target=self.start_test).start()
        
    ### _routine connetti droni  array con canali --> connessione  --> istanzia classe drogno presente e lista droni presenti

    def connect(self):
        print("provo a connettermi al drone %s " % self.name)
        self._cf.open_link(self.link_uri)
        self.connection_time = time.time()

    def close_link(self):
        self._cf.close_link()
        print("Ora chiudo con %s" %(self.ID))
        secondi = time.time() - self.connection_time
        print ("i test di %s sono durati %s secondi" % (self.name, secondi))
    
    def _crazyflie_logData_receiver(self, timestamp, data, logconf):
        # print('alle %s il crazyflie %s mi loggherebbe:' % (timestamp, self.name))
        # print(data)
        # {'health.motorPass': 15, 'health.motorTestCount': 5}
        if self.motorTestCount != None and \
            self.motorTestCount != data['health.motorTestCount'] and \
            self.test_tracker[0] == 0 :
            print(convert_motor_pass(data['health.motorPass']))
            self.propeller_test_result = convert_motor_pass(data['health.motorPass'])

            if all(self.propeller_test_result):
                self.propeller_test_passed = True
            else:
                pass

            self.test_tracker[0] = 1   ##propeller test completato
            self.battery_test()
            self.battery_test_started = True

        else:
            self.motorTestCount = data['health.motorTestCount']

        self.battery_sag        = float(data['health.batterySag'])
        self.battery_voltage    = float(data['pm.vbat'])
        self.RSSI               = float(data['radio.rssi'])
        self.firmware_revision0 = self._cf.param.get_value('firmware.revision0', 'uint32_t')
        self.firmware_revision1 = self._cf.param.get_value('firmware.revision1', 'uint16_t')

        if self.battery_test_started and self.battery_sag > 0.0:
            # print("battery test per CF %s eseguito" % self.name)
            if self.battery_sag < 0.9:
                self.battery_test_passed = True
                
                # print("battery test per CF %s passato! il valore è %s" % (self.name, self.battery_sag))
            else:
                # print("battery test per CF %s NON passato. il valore è %s" %  (self.name, self.battery_sag))
                pass
            self.test_tracker[1] = 1   # propeller test completato
            if self.battery_test_passed and self.propeller_test_passed:
                self._cf.param.set_value('ring.solidBlue', '0')
                self._cf.param.set_value('ring.solidGreen', '255')
                self._cf.param.set_value('ring.solidRed', '0')
            else:
                self._cf.param.set_value('ring.effect', '6')
                self._cf.param.set_value('ring.solidBlue', '0')
                self._cf.param.set_value('ring.solidGreen', '0')
                self._cf.param.set_value('ring.solidRed', '255')
        


def convert_motor_pass(numeroBinario):
    motori    = [1,1,1,1]
    motori[0] = (numeroBinario >> 3) & 1
    motori[1] = (numeroBinario >> 2) & 1
    motori[2] = (numeroBinario >> 1) & 1
    motori[3] = (numeroBinario >> 0) & 1
    return motori