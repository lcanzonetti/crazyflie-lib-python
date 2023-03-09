# -*- coding: utf-8 -*-

############    Generic Imports
import threading, time, sys, importlib, os
from   colorama             import Fore, Back, Style
from   colorama             import init as coloInit
coloInit(convert=True)

############    CrazyFlie Imports
from   cflib.crazyflie                            import Crazyflie
from   cflib.crazyflie.mem                        import MemoryElement
from   cflib.crazyflie.log                        import LogConfig
from   cflib.positioning.motion_commander         import MotionCommander

############    Environment Imports
from   dotenv                                     import load_dotenv
load_dotenv()

############    SYS_TEST è assoluto e va specificato nel file .env su ogni macchina
SYS_TEST_PATH      = os.environ.get('SYS_TEST_PATH')                          ### vedi sopra 
SINGLE_CF_GROUNDED = os.environ.get('SINGLE_CF_GROUNDED')
sys.path = [SYS_TEST_PATH, SINGLE_CF_GROUNDED, *sys.path]

############    Local Imports
import test_container
from   test_single_cf_grounded                    import test_link
from   common_utils                               import convert_motor_pass, write

 
class dataDrone(threading.Thread):
    def __init__(self, ID, link_uri):
        threading.Thread.__init__(self)
        self.ID                     = int(ID)
        self.link_uri               = link_uri
        self.name                   = 'dataDrone '+str(ID)
        self.test_tracker           = [0, 0, 0, 0] # val 0 = props; val 1 = battery; val 2 = leds; val 3 = radio
        self.is_testing_over        = False
        self.bandwidth              = None
        self.latency                = None
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
        self.is_connected           = False
        self.test_link              = test_link.TestLink()
        self._cf                    = Crazyflie(rw_cache='./extratech/utilities/cache_drogno_%s' %(self.ID))
        self.test_manager           = test_container.Test_Container(self, self._cf, self.ID, self.link_uri)
        self.motionCommander        = None

        self._cf.connected.add_callback(self._connected)
        self._cf.param.all_updated.add_callback(self._all_params_there)
        self._cf.fully_connected.add_callback(self._fully_connected)
        self.ledMem = self._cf.mem.get_mems(MemoryElement.TYPE_DRIVER_LED)     

    def _connected(self, link_uri):   ## callback allo scaricamento del TOC
        # self._cf.is_connected = True
        write("Mi sono connesso al drone %s all'indirizzo %s" %(self.ID, self.link_uri))
        write('TOC scaricata per il %s, in attesa dei parametri.' % (self.name))
   
    def _all_params_there(self):
        write('Parametri scaricati per %s' % self.name)
        write(Fore.LIGHTGREEN_EX + '%s connesso, it took %s seconds'% (self.name, round(time.time()-self.connection_time,2)))
        self.is_connected = True
        write("il drone %s configura il log... " % self.ID)
        self.test_manager.configura_log()
        # self.test_manager.start_sequenza_test()
        # self.test_manager.test_over_checker()

    def _fully_connected(self, link_uri):   ## callback con tutto scaricato, fa partire la sequenza test
        # self._cf.param.set_value('commander.enHighLevel', '1')

        self.motionCommander = MotionCommander(
            self._cf,
            default_height=1.0
        )

        self.firmware_revision0 = self._cf.param.get_value('firmware.revision0', 'uint32_t')
        self.firmware_revision1 = self._cf.param.get_value('firmware.revision1', 'uint16_t')
        self.firmware_modified  = self._cf.param.get_value('firmware.revision1', 'uint8_t')
 
    def connect(self):
        write("provo a connettermi al drone %s " % self.name)
        def connection():
            self._cf.open_link(self.link_uri)
            self.connection_time = time.time()
        self.connection_thread = threading.Thread(target = connection).start()

    def close_link(self):
        self._cf.close_link()
        write("Ora chiudo con %s" %(self.ID))
        secondi = time.time() - self.connection_time
        # write ("i test di %s sono durati %s secondi" % (self.name, secondi))
    
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

