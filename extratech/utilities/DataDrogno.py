import threading, time, sys
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
        self.test_tracker           = [0, 0]
        self.is_testing_over        = False
        self.propeller_test_result  = [0,0,0,0]
        self.propeller_test_passed  = False
        self.battery_test_passed    = False
        self.RSSI                   = 0
        self.channel                = None
        self.connection_time        = None
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
        self.battery_test_passed = True
        self.test_tracker[1]     = 1

    def propellerTest(self):
              
        log_conf = LogConfig(name='MotorPass', period_in_ms = 200)
        log_conf.data_received_cb.add_callback(self._crazyflie_logData_receiver)
        log_conf.add_variable('health.motorPass', 'uint8_t')
        time.sleep(2)
        self._cf.log.add_config(log_conf)
        log_conf.start()
        
        # self._cf.param.request_update_of_all_params()
        # time.sleep(2)
        print("il drone %s inizia il Propeller Test... " % self.name)
        log_conf.data_received_cb.add_callback(self.propeller_callback)

        self._cf.param.set_value('health.startPropTest', '1')
        # time.sleep(5)
        # print("Il test ha dato risultato: %s" % (self._cf.param.get_value('health.startPropTest', timeout=60)))

    def _connected(self, link_uri):   
        self._cf.is_connected = True
        print("Mi sono connesso al drone %s all'indirizzo %s" %(self.ID, self.link_uri))
        print('TOC scaricata per il %s, in attesa dei parametri.' % (self.name))
    
    # def _all_params_there(self, link_uri):
    #     print('Parametri scricati per' % self.name)

    def _fully_connected(self, link_uri):
        # self.connectToEverything()
        checker   = threading.Thread(target=self.test_checker).start()
        prop      = threading.Thread(target=self.propellerTest()).start()
        bat       = threading.Thread(target=self.battery_test()).start()
        
    ### _routine connetti droni  array con canali --> connessione  --> istanzia classe drogno presente e lista droni presenti

    def connect(self):
        print("provo a connettermi al drone %s " % self.name)
        self._cf.open_link(self.link_uri)
        self.connection_time = time.time()

    
    def close_link(self):
        self._cf.close_link()
        print("Ora chiudo con %s" %(self.ID))
        secondi = time.time() - self.connection_time
        print ("i test sono durati %s secondi" % secondi)

    def propeller_callback(self, timestamp, data, logconf):
        print("Propeller Test iniziato per il Drone %s" %(self.ID))
        # time.sleep(5)
        # motor_pass = data['health.motorPass']
        # print('Motor Pass: {}'.format(motor_pass))
        
    
    def _crazyflie_logData_receiver(self, timestamp, data, logconf):
        print('alle %s il crazyflie %s mi loggherebbe:' % (timestamp, self.name))

        if data['health.motorpass'] != 0:
            print(convert_motor_pass(data['health.motorpass']))
            self.test_tracker[0] = 1

def convert_motor_pass(numeroBinario):
    motori = [1,1,1,1]
    motori[0] = (numeroBinario >> 3) & 1
    motori[1] = (numeroBinario >> 2) & 1
    motori[2] = (numeroBinario >> 1) & 1
    motori[3] = (numeroBinario >> 0) & 1
    return motori