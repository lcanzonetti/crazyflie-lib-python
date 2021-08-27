#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Capture OSC signals and save as a .json file in current directory.
Formated as a TimeSerieBundle.
usage: python replay_osc.py -p 9000 -f test -d
"""
import sys
import time
import argparse

import liblo

from osc_recorder import CaptureOSCServer

# parser = argparse.ArgumentParser(
#     description='Capture OSC and save to .json file in current directory.')
# parser.add_argument('-p', '--port',
#                     dest='port', type=int, default=9200,
#                     help='OSC port to listen on.')
# parser.add_argument('-f', '--filename',
#                     dest='filename', type=str,
#                     default='OSC_capture',
#                     help='Name of json file to save to.')
# parser.add_argument('-d', '--debug',
#                     action='store_true', dest='debug',
#                     help='Print values captured.')

# args = parser.parse_args()
# assuming python3
import msvcrt
from itertools import cycle

loop = cycle(r"-\|/")

# replace with your function
def func():
    print("running ...", next(loop), end='\r', flush=True)


def recorda(porta, nomeDelFile, debug=False):
    try:
        server = CaptureOSCServer(porta, debug=debug)
        input("enter to start")
        server.start()
        print("Recording Server started on %d. Press q terminate and save." % (porta))
        print("Data saved to %s.json" % nomeDelFile)
        if not debug:
            print("Debug is off. Can be turned on with '-d' flag.")
    except liblo.ServerError as err:
        print(str(err))

    while True:
        try:
            time.sleep(0.1)
            func()
            if msvcrt.kbhit():
                if msvcrt.getch().lower() == b'q':
                    break
        except KeyboardInterrupt:
            time_series_bundle = server.get_time_series()
            time_series_bundle.to_json(nomeDelFile+'.json')
            server.free()
            print('Recording Done')
            # sys.exit()
    time_series_bundle = server.get_time_series()
    time_series_bundle.to_json(nomeDelFile+'.json')
    server.free()
    print('Recording Done')

# sys.exit()