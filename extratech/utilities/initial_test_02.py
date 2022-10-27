# -*- coding: utf-8 -*-
### extratech 2022
### test iniziale:
############   standard libraries 
import   time, os, sys, signal, threading, importlib

############   dependencies
import   GLOBALS                                    as     GB
import   pandas                                     as     pd
import   numpy                                      as     np
from     PIL                                        import Image, ImageDraw, ImageFont 
from     colorama              import Fore, Back, Style
from     colorama              import init as coloInit  
coloInit(convert=True)
from     dotenv                                     import load_dotenv
load_dotenv()

############    CFLIB_PATH è assoluto e va specificato nel file .env su ogni macchina
CFLIB_PATH         = os.environ.get('CFLIB_PATH')
# print(CFLIB_PATH)
sys.path = [CFLIB_PATH, *sys.path]                  ### Mette CFLIB_PATH all'inizio dele variabili d'ambiente
# print(*sys.path, sep='\n')
# cflib                   = importlib.import_module('.crazyflie', package='cflib')


import   cflib     

from     cflib.crazyflie                            import Crazyflie
from     cflib.crazyflie.syncCrazyflie              import SyncCrazyflie
from     cflib.crazyflie.mem                        import MemoryElement
from     cflib.crazyflie.mem                        import Poly4D
from     cflib.utils                                import uri_helper
from     cflib.crazyflie.log                        import LogConfig
from     cflib.utils.power_switch                   import PowerSwitch
import   cflib.crtp

############   local scripts
import   wakeUppatore, stenBaiatore
from     common_utils                               import IDFromURI, exit_signal_handler
from     test_utils                                 import istanziaClassi, check_if_test_is_completed

isExist    = os.path.exists(sys.path[3] + '/Test_Resultsss')                  ### Chekka se esiste cartella dove scrivere json dei risultati, se no la crea
if not isExist: os.makedirs(sys.path[3] + '/Test_Resultsss')

def print_greetings():
    text   = "EXTRATECH TESTING PLATFORM"
    myfont = ImageFont.truetype("verdana.ttf", 8, encoding="unic")
    text_width, text_height   = myfont.getsize(text)
    img    = Image.new("1",(text_width, text_height),"black")
    draw   = ImageDraw.Draw(img)
    draw.text((0, 0), text, "white", font=myfont)
    pixels = np.array(img, dtype=np.uint8)
    chars = np.array([' ','#'], dtype="U1")[pixels]
    strings = chars.view('U' + str(chars.shape[1])).flatten()
    print( "\n".join(strings))
    print('\n')

def main():
    print_greetings()

    time.sleep(2)
    
    cflib.crtp.init_drivers()
    wakeUppatore.wekappa()
    try:
        scan_for_crazyflies()
    except Exception as e:
        print(".")
    signal.signal(signal.SIGINT, exit_signal_handler)
    
    istanziaClassi()
    check_if_completed = threading.Thread(target=check_if_test_is_completed).start()

if __name__ == '__main__':
    try:
        main()
        while not GB.is_test_completed:
            time.sleep(1)
            pass
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    
  


















# Initiate the low level drivers

### _routine componi indirizzi completi:   array indirizzi --> array con canali

### _routine connessione  prendi da un pool di thread e provi. 

###  routine esegui test:      prendono istanza da lista drone, fa partire i test e controlla che siano finiti, infine fa partire la stampa
### _test batteria             prendono istanza da lista drone, fa il check, scrive il risultato 

### _test radio (verificare un buon valore)  prendono istanza da lista drone, fa il check, scrive il risultato 

## _funzione stampa             prendono istanza da lista droni presenti - stampa i risultati (e dato riassuntivo)
