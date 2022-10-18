import os, threading, multiprocessing
from   sqlite3 import connect
from   dotenv  import load_dotenv
load_dotenv()
ROOT_DIR                   = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))


######################################    OPTIONS
WE_ARE_FAKING_IT           = False
PRINTING_ENABLED           = False
LOGGING_ENABLED            = True
AUTO_RECONNECT             = False
INITIAL_TEST               = False
AGGREGATION_ENABLED        = False

######################################    NETWORK
FEEDBACK_SENDING_IP        = "192.168.10.160"   ##  to whom we send OSC telemetry to
FEEDBACK_SENDING_PORT      = 9203
FEEDBACK_ENABLED           = True
COMPANION_FEEDBACK_IP      = os.getenv("COMPANION_FEEDBACK_IP")    ##  COMPANION TELEMETRY AND STATUS UPDATES
COMPANION_FEEDBACK_PORT    = 12321
COMPANION_FEEDBACK_ENABLED = True

######################################    COMPANION GUI SETTINGS
COMPANION_PAGES             = ['92', '93', '94']
TC_COMPANION_PAGE           = '91'
SWARM_PAGE                  = '90'
COMPANION_ENABLE_BUTTON     = '25'
COMPANION_UPDATE_RATE       = 2
GLOBAL_FREQUENCY            = 0.9

######################   osc receiving:
RECEIVING_IP                = "0.0.0.0"
RECEIVING_PORT              = 9200

######################################    COSTANTI SPAZIALI E DI VOLO
BOX_X                       = 2.3
BOX_Y                       = 2.8
BOX_Z                       = 2.4
RELATIVE_SPACING            = 0.4
DEFAULT_HEIGHT              = 0.8
DEFAULT_VELOCITY            = 0.85
DEFAULT_SCRAMBLING_TIME     = 2.2
SPACING                     = 0.4
CLAMPING                    = True
LIGHTHOUSE_METHOD           = '0'

##################################################  global rates:
LOGGING_FREQUENCY                = 1000
RECEIVED_MESSAGES_SAMPLING_RATE  = 10
RING_FADE_TIME                   = 0.001
RECONNECT_FREQUENCY              = 1
OSC_PROCESS_RATE                 = 0.1

###################     BATTERY
BATTERY_CHECK_RATE          = 0.5
BATTERY_WARNING_LEVEL       = 3.45
BATTERY_DRAINED_LEVEL       = 3.2

######################################             GLOBAL RATES AND VARIABLES
print_rate               = 1.1
commandsFrequency        = 0.1   # actual command'd rate to uavss
lastRecordPath           = ''  
we_may_send              = False
drogni = {}

######################################    EVENTS TO EXIT 
def singleton(cls):
    return cls()

@singleton
class Eventi():
        def __init__(self):
                self.threads_exit_event   = None
                self.processes_exit_event = None
        def run(self):
                # print('\ninizializzo gli eventi')
                self.threads_exit_event               = threading.Event()
                self.processes_exit_event             = multiprocessing.Event()
        def get_thread_exit_event(self):
                return self.threads_exit_event
        def get_process_exit_event(self):
                return self.processes_exit_event
        def set_thread_exit_event(self):
                self.threads_exit_event.set()
        def set_process_exit_event(self):
                self.processes_exit_event.set()

eventi = Eventi
eventi.run()



connected_uris = []
################################################## uris to be woke up at startup
uris = [    
        # 'radio://0/80/2M/E7E7E7E7E0',
        # 'radio://0/80/2M/E7E7E7E7E1',
        # 'radio://0/80/2M/E7E7E7E7E2',
        # 'radio://0/90/2M/E7E7E7E7E3',
        # 'radio://1/120/2M/E7E7E7E7E4', 
        # 'radio://0/80/2M/E7E7E7E7E5',
        # 'radio://0/100/2M/E7E7E7E7E6',
        # 'radio://3/100/2M/E7E7E7E7E7',
        # 'radio://1/100/2M/E7E7E7E7E8', 
        # 'radio://2/110/2M/E7E7E7E7E9',
        # 'radio://0/110/2M/E7E7E7E7EA',
        # 'radio://0/120/2M/E7E7E7E7EB',
        # 'radio://0/120/2M/E7E7E7E7EC',
        # 'radio://0/120/2M/E7E7E7E7ED',
        # 'radio://0/120/2M/E7E7E7E7EE',
        # 'radio://0/120/2M/E7E7E7E7EF',
        ]
        
#########################################################################
uri_map = \
{    
   "0":     'radio://0/80/2M/E7E7E7E7E0',
   "1":     'radio://0/80/2M/E7E7E7E7E1',
   "2":     'radio://0/80/2M/E7E7E7E7E2',
   "3":     'radio://0/90/2M/E7E7E7E7E3',
   "4":     'radio://1/120/2M/E7E7E7E7E4', 
   "5":     'radio://0/80/2M/E7E7E7E7E5',
   "6":     'radio://0/100/2M/E7E7E7E7E6',
   "7":     'radio://3/100/2M/E7E7E7E7E7',
   "8":     'radio://1/100/2M/E7E7E7E7E8', 
   "9":     'radio://2/110/2M/E7E7E7E7E9',
   "A":     'radio://0/110/2M/E7E7E7E7EA',
   "B":     'radio://0/120/2M/E7E7E7E7EB',
   "C":     'radio://0/120/2M/E7E7E7E7EC',
   "D":     'radio://0/120/2M/E7E7E7E7ED',
   "E":     'radio://0/120/2M/E7E7E7E7EE',
   "F":     'radio://0/120/2M/E7E7E7E7EF',
}



PREFERRED_STARTING_POINTS =   [
                                 [ -SPACING, SPACING],    [0, SPACING]   , [SPACING, SPACING], 
                                 [ -SPACING, -0],          [0, 0]         , [SPACING, 0], 
                                 [ -SPACING, -SPACING],    [0, -SPACING]  , [SPACING, -SPACING], 
                                 [ -SPACING*1.5, -SPACING], [0, 0], [0,0] , [0,0], [0,0], [0,0], [0,0]
                               ]