from cflib.bootloader import Bootloader


import os
import subprocess
import GLOBALS as GB
from     colorama              import Fore, Back, Style
from     colorama              import init as coloInit 
from     common_utils          import write, IDFromURI
import threading

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

def flasha_firmware_subprocess(drogno):
  subprocess.run(['cd', '{}'.format(GB.CF_CLIENT_PATH), '&&', 'python', 'bin/cfloader', 'flash', '{}'.format(GB.FILE_TO_FLASH), 'stm32-fw', '-w', '{}'.format(drogno)], shell=True, stdout=open(os.path.join(__location__, "log.txt"), mode="a"))
  write("Drone %s correctly flashed!" % IDFromURI(drogno))

  # threading.Thread(target=flasha_thread).start()

if __name__ == "__main__":
    flasha_firmware_subprocess("radio://0/80/2M/E7E7E7E702")
    
