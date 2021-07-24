# -*- coding: utf-8 -*-

from osc4py3.as_eventloop import *
from osc4py3 import oscmethod as osm

def handlerfunction(address, s, x, y):
    print (address, s, x, y)
    pass

# Start the system.
osc_startup()

# Make server channels to receive packets.
# osc_udp_server(9200, "aservername")
osc_udp_server("0.0.0.0", 9200, "pino")

osc_method("/d3/*", handlerfunction, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)

# Periodically call osc4py3 processing method in your event loop.
finished = False
while not finished:
    # …
    osc_process()
    # …

# Properly close the system.
osc_terminate()