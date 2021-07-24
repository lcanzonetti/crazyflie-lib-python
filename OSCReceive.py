# -*- coding: utf-8 -*-

from osc4py3.as_eventloop import *
from osc4py3 import oscmethod as osm

def handlerfunction(s, x, y):
    # Will receive message data unpacked in s, x, y
    print (s, x, y)
    pass

def handlerfunction2(address, s, x, y):
    # Will receive message address, and message data flattened in s, x, y
    print (address, s, x, y)
    pass

# Start the system.
osc_startup()

# Make server channels to receive packets.
# osc_udp_server(9200, "aservername")
osc_udp_server("0.0.0.0", 9200, "pino")

# Associate Python functions with message address patterns, using default
# argument scheme OSCARG_DATAUNPACK.
osc_method("/test/*", handlerfunction)
# Too, but request the message address pattern before in argscheme
osc_method("/test/*", handlerfunction2, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)

# Periodically call osc4py3 processing method in your event loop.
finished = False
while not finished:
    # …
    osc_process()
    # …

# Properly close the system.
osc_terminate()