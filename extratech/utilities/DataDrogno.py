# -*- coding: utf-8 -*-

import threading, time, sys, importlib
test_single_cf_grounded = importlib.import_module('test_single_cf_grounded')
cflib                   = importlib.import_module('cflib')

from   cflib.crazyflie                            import Crazyflie
from   cflib.crazyflie.syncCrazyflie              import SyncCrazyflie
from   cflib.crazyflie.mem                        import MemoryElement
from   cflib.crazyflie.mem                        import Poly4D
from   cflib.utils                                import uri_helper
import cflib.crtp
from   cflib.crazyflie.log                        import LogConfig
from   test_single_cf_grounded import test_link


 
class dataDrone(threading.Thread):
    def __init__(self, ID, link_uri):
        threading.Thread.__init__(self)
        self.ID                     = int(ID)
        self.link_uri               = link_uri
        self.name                   = 'dataDrone '+str(ID)
        self.test_tracker           = [0, 0, 0, 0] # val 0 = props; val 1 = battery; val 2 = leds; val 3 = radio
        self.is_testing_over        = False
        self.propeller_test_result  = [0,0,0,0]
        self.battery_test_started   = False
        self.propeller_test_passed  = False
        self.battery_test_passed    = False
        self.lampeggio_finito       = False     ### True se il led di notifica risultati ha finito di lampeggiare
        self.battery_sag            = 0.0
        self.battery_voltage        = 0.0
        self.RSSI                   = 0
        self.firmware_revision0     = 0
        self.firmware_revision1     = 0
        self.channel                = None
        self.connection_time        = None
        self.current_motorTestCount = None
        self.new_motorTestCount     = None
        self.firmware0              = None
        self.firmware1              = None
        self.firmware_modified      = None
        self.test_link              = test_link.TestLink()
        self._cf                    = Crazyflie(rw_cache='./extratech/utilities/cache_drogno_%s' %(self.ID))
        self._cf.connected.add_callback(self._connected)
        self._cf.fully_connected.add_callback(self._fully_connected)
        self.ledMem = self._cf.mem.get_mems(MemoryElement.TYPE_DRIVER_LED)

    ### Incapsulato cambi colore in funzioni 
    def fai_rosso(self):
        self._cf.param.set_value('ring.effect', '7')
        self._cf.param.set_value('ring.solidRed', '255')
        self._cf.param.set_value('ring.solidGreen', '0')
        self._cf.param.set_value('ring.solidBlue', '0')
    
    def fai_verde(self):
        self._cf.param.set_value('ring.effect', '7')
        self._cf.param.set_value('ring.solidRed', '0')
        self._cf.param.set_value('ring.solidGreen', '255')
        self._cf.param.set_value('ring.solidBlue', '0')
    
    def fai_blu(self):
        self._cf.param.set_value('ring.effect', '7')
        self._cf.param.set_value('ring.solidRed', '0')
        self._cf.param.set_value('ring.solidGreen', '0')
        self._cf.param.set_value('ring.solidBlue', '255')
    
    def spegni_led(self):
        self._cf.param.set_value('ring.effect', '7')
        self._cf.param.set_value('ring.solidRed', '0')
        self._cf.param.set_value('ring.solidGreen', '0')
        self._cf.param.set_value('ring.solidBlue', '0')

    def test_over_checker(self):
        while not self.is_testing_over:
            if not (all ( x != 0 for x in self.test_tracker)):
                time.sleep(1)
                pass
            else:
                self.is_testing_over = True
                if self.battery_test_passed and self.propeller_test_passed:
                    self.fai_verde()
                    time.sleep(10)
                    self.lampeggio_finito = True
                else:
                    for i in range(20):
                        if i % 2 == 0:
                            self.fai_rosso()
                            time.sleep(0.5)
                        else:
                            self.spegni_led()
                            time.sleep(0.5)
                    self.lampeggio_finito = True
                print ("test finiti per CF %s " % self.name)
                print ("Il firmware corrente è una roba tipo: %s %s modificato? -> %s" %(self.firmware_revision0, self.firmware_revision1, self.firmware_modified))
                self.close_link()
    
    def radio_test(self):
        self.test_link.bandwidth(self.link_uri)
        self.test_link.latency(self.link_uri)

    def led_test(self):
        def led_test_sequence():
            self.spegni_led()
            time.sleep(1)
            # Set solid color effect
            self.fai_rosso()
            time.sleep(2)
            self.fai_verde()
            time.sleep(2)
            self.fai_blu()
            time.sleep(2)
            self.spegni_led()
            time.sleep(2)
            # # Set fade to color effect
            # self._cf.param.set_value('ring.effect', '14')
            # # Set fade time i seconds
            # self._cf.param.set_value('ring.fadeTime', '1.0')
            # # Set the RGB values in one uint32 0xRRGGBB
            # self._cf.param.set_value('ring.fadeColor', int('0000A0', 16))
            # time.sleep(1)
            # self._cf.param.set_value('ring.fadeColor', int('00A000', 16))
            # time.sleep(1)
            # self._cf.param.set_value('ring.fadeColor', int('A00000', 16))
            # time.sleep(1)
            print('led test finito')
            self.test_tracker[2] = 1   # led test completato
        threading.Thread(target=led_test_sequence).start()

    def battery_test(self):
        self._cf.param.set_value('health.startBatTest', '1')
        def batt_control_loop():
            while self.battery_sag == 0.0:
                time.sleep(0.3)
            print("il drone %s ha finito il Battery Test. " % self.name)
            if self.battery_sag < 0.9:
                self.battery_test_passed = True
                print("battery test per CF %s passato! il valore è %s" % (self.name, self.battery_sag))
            else:
                print("battery test per CF %s NON passato. il valore è %s" %  (self.name, self.battery_sag))
            self.test_tracker[1] = 1   # battery test completato
        threading.Thread(target=batt_control_loop).start()

    def propeller_test(self):
        self._cf.param.set_value('health.startPropTest', '1')
        def prop_control_loop():
            while   self.new_motorTestCount     == None                         or  \
                    self.current_motorTestCount == None:                       
                time.sleep(0.3)
            while (self.new_motorTestCount - self.current_motorTestCount) != 1:
                time.sleep(0.3)
                # print(str(self.new_motorTestCount) + ' ' + str(self.current_motorTestCount))
            print("il drone %s ha finito il Propeller Test. " % self.name)

            time.sleep(1)
            if all (self.propeller_test_result):                ### Resituisce True solo se tutti i risultati motori stanno a '1'
                self.propeller_test_passed = True
                

            self.test_tracker[0] = 1   ##propeller test completato
        threading.Thread(target=prop_control_loop).start()
     
    def configura_log(self):
        log_conf = LogConfig(name='MotorPass', period_in_ms = 500)
        log_conf.data_received_cb.add_callback(self._crazyflie_logData_receiver)
        log_conf.add_variable('health.motorPass', 'uint8_t')
        log_conf.add_variable('health.motorTestCount', 'uint16_t')
        log_conf.add_variable('pm.vbat', 'FP16')
        log_conf.add_variable('radio.rssi',    'uint8_t')
        log_conf.add_variable('health.batterySag', 'FP16')
        self._cf.log.add_config(log_conf)
        # time.sleep(0.5)
        log_conf.start()

    def start_sequenza_test(self):       ### sequenza principale con tempi

        self.fai_blu()                  ### Blue is for testing

        print("il drone %s configura il log... " % self.name)
        self.configura_log()

        print("il drone %s inizia il Propeller Test... " % self.name)
        self.propeller_test()

        time.sleep(7)

        print("il drone %s inizia il battery test... " % self.name)
        self.battery_test()

        time.sleep(1.5)

        print("il drone %s inizia il led test... " % self.name)
        self.led_test()

        time.sleep(1.5)

        print("il drone %s inizia i test radio... " % self.name)
        self.radio_test()       

    def _connected(self, link_uri):   ## callback allo scaricamento del TOC
        self._cf.is_connected = True
        print("Mi sono connesso al drone %s all'indirizzo %s" %(self.ID, self.link_uri))
        print('TOC scaricata per il %s, in attesa dei parametri.' % (self.name))

    def _fully_connected(self, link_uri):   ## callback con tutto scaricato, fa partire la sequenza test
        # self.connectToEverything()
        checker           = threading.Thread(target=self.test_over_checker).start()
        start_test_thread = threading.Thread(target=self.start_sequenza_test).start()
        self.firmware_revision0 = self._cf.param.get_value('firmware.revision0', 'uint32_t')
        self.firmware_revision1 = self._cf.param.get_value('firmware.revision1', 'uint16_t')
        self.firmware_modified  = self._cf.param.get_value('firmware.revision1', 'uint8_t')
        
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
        # qualche assegnazione di variabile:
        self.battery_sag           = float(data['health.batterySag'])
        self.battery_voltage       = float(data['pm.vbat'])
        self.propeller_test_result = convert_motor_pass(data['health.motorPass'])

        if self.current_motorTestCount   == None: self.current_motorTestCount = data['health.motorTestCount']
        else:                                     self.new_motorTestCount     = data['health.motorTestCount']

        self.battery_sag        = float(data['health.batterySag'])
        self.battery_voltage    = float(data['pm.vbat'])
        self.RSSI               = float(data['radio.rssi'])
 
def convert_motor_pass(numeroBinario):
    motori    = [1,1,1,1]
    motori[0] = (numeroBinario >> 3) & 1
    motori[1] = (numeroBinario >> 2) & 1
    motori[2] = (numeroBinario >> 1) & 1
    motori[3] = (numeroBinario >> 0) & 1
    return motori

