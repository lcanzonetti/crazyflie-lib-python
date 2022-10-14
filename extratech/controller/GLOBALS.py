lastRecordPath        = ''  
WE_ARE_FAKING_IT      = False
LOGGING_ENABLED       = True
AUTO_RECONNECT        = False
RECONNECT_FREQUENCY   = 1
COMMANDS_FREQUENCY    = 0.1
FEEDBACK_SENDING_PORT = 6000
BROADCAST_IP          = "192.168.1.21"
BOX_X                   = 2.3
BOX_Y                   = 2.8
BOX_Z                   = 2.4
LIGHTHOUSE_METHOD       = '0'
DEFAULT_HEIGHT          = 0.8
DEFAULT_VELOCITY        = 0.85
DEFAULT_SCRAMBLING_TIME = 2.2
RELATIVE_SPACING        = 0.4
BATTERY_CHECK_RATE      = 0.5
STATUS_PRINT_RATE       = 1.1
LOGGING_FREQUENCY       = 1000
FEEDBACK_SENDING_IP     = '127.0.0.1'
FEEDBACK_SENDING_PORT   = 9203
FEEDBACK_ENABLED        = True
CLAMPING                = True
RING_FADE_TIME          = 0.001
INITIAL_TEST            = False
BATTERY_WARNING_LEVEL   = 3.45
BATTERY_DRAINED_LEVEL   = 3.2

drogni = {}

#########################################################################
uris = [    
        # 'radio://0/80/2M/E7E7E7E7E0',
        'radio://0/80/2M/E7E7E7E7E1',
        # 'radio://0/80/2M/E7E7E7E7E2',
        'radio://0/90/2M/E7E7E7E7E3',
        # 'radio://1/120/2M/E7E7E7E7E4', 
        'radio://0/80/2M/E7E7E7E7E5',
        'radio://0/100/2M/E7E7E7E7E6',
        # 'radio://3/100/2M/E7E7E7E7E7',
        # 'radio://2/100/2M/E7E7E7E7E8', 
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
   "8":     'radio://2/100/2M/E7E7E7E7E8', 
   "9":     'radio://2/110/2M/E7E7E7E7E9',
   "A":     'radio://0/110/2M/E7E7E7E7EA',
   "B":     'radio://0/120/2M/E7E7E7E7EB',
   "C":     'radio://0/120/2M/E7E7E7E7EC',
   "D":     'radio://0/120/2M/E7E7E7E7ED',
   "E":     'radio://0/120/2M/E7E7E7E7EE',
   "F":     'radio://0/120/2M/E7E7E7E7EF',
}
SPACING = 0.4

PREFERRED_STARTING_POINTS =   [ ( -SPACING, SPACING),    (0, SPACING)   , (SPACING, SPACING), 
                                ( -SPACING, -0),         (0, 0)         , (SPACING, 0), 
                                ( -SPACING, -SPACING),   (0, -SPACING)  , (SPACING, -SPACING), 
                                ( -SPACING*1.5, -SPACING), (0, 0), (0,0) , (0,0), (0,0), (0,0), (0,0)
                                ]

