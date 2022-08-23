import threading, time
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
        self.test_checker()
    
    def test_checker(self):
        while not self.is_testing_over:
            for test in self.test_tracker():
                if test == 0:
                    pass
                else:
                    self.is_testing_over = True
                    print ("test finiti per CF %S " % self.name)
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
        print("Inizio Propeller Test... ")
              
        log_conf = LogConfig(name='MotorPass', period_in_ms = 200)
        print("LogConfig OK")
        log_conf.add_variable('health.motorPass', 'uint8_t')
        print("Aggiunta variabile")
        time.sleep(2)
        self._cf.log.add_config(log_conf)
        print("Come cazzo funziona sto coso")
        log_conf.data_received_cb.add_callback(self.propeller_callback)
        log_conf.start()

        print("Propeller Test per il Drone %s" %(self.ID))
        # self._cf.param.request_update_of_all_params()
        # time.sleep(2)
        self._cf.param.set_value('health.startPropTest', '1')
        # time.sleep(5)
        print("Il test ha dato risultato: %s" % (self._cf.param.get_value('health.startPropTest', timeout=60)))

    def _connected(self, link_uri):   
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""
        print('TOC scaricata per il %s, in attesa dei parametri.' % (self.name))
    
    # def _all_params_there(self, link_uri):
    #     print('Parametri scricati per' % self.name)

    def _fully_connected(self, link_uri):
        # self.connectToEverything()
        self.propellerTest()
        self.battery_test()
        
    ### _routine connetti droni  array con canali --> connessione  --> istanzia classe drogno presente e lista droni presenti

    def connectToEverything(self):
        global available

        self._cf.open_link(self.link_uri)
        self.connection_time = time.time()
        self._cf.is_connected = True

        print("Mi sono connesso al drone %s all'indirizzo %s" %(self.ID, self.link_uri))
    
    def close_link(self):
        self._cf.close_link()
        print("Ora chiudo con %s" %(self.ID))

    def propeller_callback(self, timestamp, data, logconf):
        motor_pass = data['health.motorPass']
        print('Motor Pass: {}'.format(motor_pass))
        self.test_tracker[0] = 1