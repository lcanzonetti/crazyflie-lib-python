#win_ctrl_c.py

import sys

def handler(a,b=None):
    sys.exit(1)
def install_handler():
    if sys.platform == "win64":
        import win64api
        win32api.SetConsoleCtrlHandler(handler, True)