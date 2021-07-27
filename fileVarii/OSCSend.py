
# Import needed modules from osc4py3
from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse

ip   = "192.168.10.255"
port = 9201

# Start the system.
osc_startup()

# Make client channels to send packets.
gino = osc_udp_client(ip, port, "drognoBack")
print('osc initalized on', ip, port)


# Build a simple message and send it.
msg = oscbuildparse.OSCMessage("/test/me", ",sif", ["text", 672, 8.871])
osc_send(msg, "drognoBack")

msg = oscbuildparse.OSCMessage("/test/me", ",sif", ["text", 672, 8.871])
osc_send(msg, "drognoBack")

msg = oscbuildparse.OSCMessage("/test/me", ",sif", ["text", 672, 8.871])
osc_send(msg, "drognoBack")


def sendRotation(droneID, roll, pitch, yaw):
    msg = oscbuildparse.OSCMessage("/drogni/"+str(droneID), None, [roll, pitch, yaw])
    osc_send(msg, "drognoBack")
    print (roll, pitch, yaw)

