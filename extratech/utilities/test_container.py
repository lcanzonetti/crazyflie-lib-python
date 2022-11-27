############    Generic Imports
import threading, time, sys, importlib, os, subprocess

############    CrazyFlie Imports
import cflib
import cflib.crtp
from   cflib.crazyflie                            import Crazyflie
from   cflib.crazyflie.mem                        import MemoryElement
from   cflib.crazyflie.log                        import LogConfig

############    Environment Imports
from   dotenv                                     import load_dotenv
load_dotenv()

############    SYS_TEST è assoluto e va specificato nel file .env su ogni macchina
SYS_TEST_PATH      = os.environ.get('SYS_TEST_PATH')                          ### vedi sopra 
SINGLE_CF_GROUNDED = os.environ.get('SINGLE_CF_GROUNDED')
sys.path = [SYS_TEST_PATH, SINGLE_CF_GROUNDED, *sys.path]

############    Local Imports
from   test_single_cf_grounded                    import test_link
from   common_utils                               import convert_motor_pass
import GLOBALS as GB

class Test_Container():
    def __init__(self, parent_drogno, cf, ID, link_uri):
        self.ID = ID
        print(self.ID)
        self.cf = cf
        print(self.cf)
        self.parent_drogno = parent_drogno
        print(self.parent_drogno)
        self.link_uri = link_uri

    def fai_rosso(self):
        self.cf.param.set_value('ring.effect', '7')
        self.cf.param.set_value('ring.solidRed', '255')
        self.cf.param.set_value('ring.solidGreen', '0')
        self.cf.param.set_value('ring.solidBlue', '0')
    
    def fai_verde(self):
        self.cf.param.set_value('ring.effect', '7')
        self.cf.param.set_value('ring.solidRed', '0')
        self.cf.param.set_value('ring.solidGreen', '255')
        self.cf.param.set_value('ring.solidBlue', '0')
    
    def fai_blu(self):
        self.cf.param.set_value('ring.effect', '7')
        self.cf.param.set_value('ring.solidRed', '0')
        self.cf.param.set_value('ring.solidGreen', '0')
        self.cf.param.set_value('ring.solidBlue', '255')
    
    def spegni_led(self):
        self.cf.param.set_value('ring.effect', '7')
        self.cf.param.set_value('ring.solidRed', '0')
        self.cf.param.set_value('ring.solidGreen', '0')
        self.cf.param.set_value('ring.solidBlue', '0')

    def test_over_checker(self):
        def thread_over_checker():
            while not self.parent_drogno.is_testing_over:
                if not (all ( x != 0 for x in self.parent_drogno.test_tracker)):
                    # print("test over sta")
                    time.sleep(1)
                    pass
                else:
                    self.parent_drogno.is_testing_over = True
                    if self.parent_drogno.battery_test_passed and self.parent_drogno.propeller_test_passed:
                        self.fai_verde()
                        time.sleep(10)
                        self.parent_drogno.lampeggio_finito = True
                    else:
                        for i in range(20):
                            if i % 2 == 0:
                                self.fai_rosso()
                                time.sleep(0.5)
                            else:
                                self.spegni_led()
                                time.sleep(0.5)
                        self.parent_drogno.lampeggio_finito = True
                    print ("test finiti per CF %s " % self.parent_drogno.name)
                    print ("Il firmware corrente è una roba tipo: %s %s modificato? -> %s" %(self.parent_drogno.firmware_revision0, self.parent_drogno.firmware_revision1, self.parent_drogno.firmware_modified))
                    
                    print ("Controlliamo un po' i firmware e se serve aggiorniamoli... ")

                    # self.cf.close_link()
        threading.Thread(target=thread_over_checker).start()
    
    def radio_test(self):
        self.parent_drogno.bandwidth = self.parent_drogno.test_link.bandwidth(self.link_uri)
        self.parent_drogno.latency   = self.parent_drogno.test_link.latency(self.link_uri)

        print('radio test finito')                          
        self.cf.param.set_value('ring.effect', '7')            ### Fai violetto se test radio finito
        self.cf.param.set_value('ring.solidRed', '100')
        self.cf.param.set_value('ring.solidGreen', '0')
        self.cf.param.set_value('ring.solidBlue', '100')
        time.sleep(3)
        self.spegni_led()
        self.parent_drogno.test_tracker[3] = 1
        print(self.parent_drogno.test_tracker)

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
            self.parent_drogno.test_tracker[2] = 1   # led test completato
            print(self.parent_drogno.test_tracker)
        threading.Thread(target=led_test_sequence).start()

    def battery_test(self):
        try:
            self.cf.param.set_value('health.startBatTest', '1')
        except IndexError:
            print()
        def batt_control_loop():
            while self.parent_drogno.battery_sag == 0.0:
                time.sleep(0.3)
            print("il drone %s ha finito il Battery Test. " % self.parent_drogno.name)
            if self.parent_drogno.battery_sag < 0.9:
                self.parent_drogno.battery_test_passed = True
                print("battery test per CF %s passato! il valore è %s" % (self.parent_drogno.name, self.parent_drogno.battery_sag))
            else:
                print("battery test per CF %s NON passato. il valore è %s" %  (self.parent_drogno.name, self.parent_drogno.battery_sag))
            self.parent_drogno.test_tracker[1] = 1   # battery test completato
            print(self.parent_drogno.test_tracker)
        threading.Thread(target=batt_control_loop).start()

    def propeller_test(self):
        self.cf.param.set_value('health.startPropTest', '1')
        def prop_control_loop():
            while   self.parent_drogno.new_motorTestCount     == None                         or  \
                    self.parent_drogno.current_motorTestCount == None:                       
                time.sleep(0.3)
            while (self.parent_drogno.new_motorTestCount - self.parent_drogno.current_motorTestCount) != 1:
                time.sleep(0.3)
                # print(str(self.new_motorTestCount) + ' ' + str(self.current_motorTestCount))
            print("il drone %s ha finito il Propeller Test. " % self.parent_drogno.name)

            time.sleep(1)
            if all (self.parent_drogno.propeller_test_result):                ### Resituisce True solo se tutti i risultati motori stanno a '1'
                self.parent_drogno.propeller_test_passed = True
                

            self.parent_drogno.test_tracker[0] = 1   ##propeller test completato
            print(self.parent_drogno.test_tracker)
        threading.Thread(target=prop_control_loop).start()
     
    def configura_log(self):
        log_conf = LogConfig(name='MotorPass', period_in_ms = 500)
        log_conf.data_received_cb.add_callback(self.parent_drogno._crazyflie_logData_receiver)
        log_conf.add_variable('health.motorPass', 'uint8_t')
        log_conf.add_variable('health.motorTestCount', 'uint16_t')
        log_conf.add_variable('pm.vbat', 'FP16')
        log_conf.add_variable('radio.rssi', 'uint8_t')
        log_conf.add_variable('health.batterySag', 'FP16')
        self.cf.log.add_config(log_conf)
        # time.sleep(0.5)
        log_conf.start()

    def start_sequenza_test(self):       ### sequenza principale con tempi

        def thread_sequenza_test():

            self.fai_blu()                   ### Blue is for testing

            print("il drone %s configura il log... " % self.parent_drogno.name)
            self.configura_log()

            print("il drone %s inizia il Propeller Test... " % self.parent_drogno.name)
            self.propeller_test()

            time.sleep(7)

            print("il drone %s inizia il battery test... " % self.parent_drogno.name)
            self.battery_test()

            time.sleep(1.5)

            print("il drone %s inizia il led test... " % self.parent_drogno.name)
            self.led_test()

            time.sleep(10)                                                 ### Attende che il test led sia finito prima di chiamare test radio

            print("il drone %s inizia i test radio... " % self.parent_drogno.name)
            self.radio_test()
        
        threading.Thread(target=thread_sequenza_test).start()