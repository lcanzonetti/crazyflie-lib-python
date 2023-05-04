import os
import subprocess
import GLOBALS as GB
from     colorama              import Fore, Back, Style
from     colorama              import init as coloInit 
from     common_utils          import write, IDFromURI
import threading

def flasha_firmware_subprocess(drogno):
  def flasha_thread():
    write("Adesso flashiamo tutti i droni che ne hanno bisogno!")
    write('\n')

    subprocess.run(['wsl', 'cd', '{}'.format(GB.CF_FIRMWARE_PATH), ';', 'make', 'cload', 'CLOAD_CMDS=-w {}'.format(drogno)],   shell=True)
    write('\n')
    write("Drone %s flashato!" % IDFromURI(drogno))

  threading.Thread(target=flasha_thread).start()

if __name__ == "__main__":
    # fai_cose_in_wsl()
    for drogno in GB.available:
    
      flasha_firmware_subprocess(drogno)