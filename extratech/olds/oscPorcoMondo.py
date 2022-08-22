# Import needed modules from osc4py3
from   osc4py3.as_eventloop import *
from   osc4py3               import oscmethod as osm
from osc4py3 import oscbuildparse
import time

import logging

logging.basicConfig(format='%(asctime)s - %(threadName)s ø %(name)s - ' '%(levelname)s - %(message)s')
logger = logging.getLogger("osc")
logger.setLevel(logging.DEBUG)
# Start the system.
osc_startup(logger=logger)

# Make client channels to send packets.
osc_broadcast_client("192.168.1.255", 12321, "aclientname")



# Build a simple message and send it.
msg = oscbuildparse.OSCMessage("/style/bgcolor/92/7", ",iii", [128,90,230])
msg2 = oscbuildparse.OSCMessage("/style/text/92/6", ",s", ['porco dio'])
osc_send(msg, "aclientname")
osc_send(msg2, "aclientname")



# Buils a complete bundle, and postpone its executions by 10 sec.
exectime = time.time() + 10   # execute in 10 seconds
msg1 = oscbuildparse.OSCMessage("/sound/levels", None, [1, 5, 3])
msg2 = oscbuildparse.OSCMessage("/sound/bits", None, [32])
msg3 = oscbuildparse.OSCMessage("/sound/freq", None, [42000])
bun = oscbuildparse.OSCBundle(oscbuildparse.unixtime2timetag(exectime),
                    [msg1, msg2, msg3])
osc_send(bun, "aclientname")

# Periodically call osc4py3 processing method in your event loop.
finished = False
while not finished:
    # You can send OSC messages from your event loop too…
    # …
    # Build a message with autodetection of data types, and send it.
    msg = oscbuildparse.OSCMessage("/test/me", None, ["text", 672, 8.871])
    osc_send(msg, "aclientname")
    osc_process()
    time.sleep(1)
    # …

# Properly close the system.
osc_terminate()