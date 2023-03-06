import os
import subprocess
import GLOBALS as GB
from     colorama              import Fore, Back, Style
from     colorama              import init as coloInit 

available = [
    "radio://0/80/2M/E7E7E7E7E1",
  # "radio://0/100/2M/E7E7E7E7E6",
  # "radio://0/100/2M/E7E7E7E7E8"
]

# def fai_cose_in_wsl():
#     # os.system('wsl -e sh -c "cd {}; make cload"'.format(GB.CF_FIRMWARE_PATH))
#     os.system('wsl cd {}'.format(GB.CF_FIRMWARE_PATH))
#     # os.system('wsl make menuconfig')

def flasha_firmware_subprocess():

    print("Adesso flashiamo tutti i droni che ne hanno bisogno!")
    print('\n')

    for drogno in available:
        subprocess.run(['wsl', 'cd', '{}'.format(GB.CF_FIRMWARE_PATH), ';', 'make', 'cload', 'CLOAD_CMDS=-w {}'.format(drogno)], shell=True)
        print('\n')

if __name__ == "__main__":
    # fai_cose_in_wsl()
    flasha_firmware_subprocess()