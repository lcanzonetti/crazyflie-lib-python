
# Import needed modules from osc4py3
from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse

ip   = "192.168.10.255"
port = 9201

# Start the system.
osc_startup()

# Make client channels to send packets.
gino = osc_broadcast_client(ip, port, "drognoBack")
print('osc initalized on', ip, port)


# Build a simple message and send it.
# msg = oscbuildparse.OSCMessage("/test/me", ",sif", ["ma", 672, 8.871])
# osc_send(msg, "drognoBack")

# msg = oscbuildparse.OSCMessage("/test/me", ",sif", ["porco", 672, 8.871])
# osc_send(msg, "drognoBack")

# msg = oscbuildparse.OSCMessage("/test/me", ",sif", ["il clero", 672, 8.871])
# osc_send(msg, "drognoBack")


def sendRotation(droneID, roll, pitch, yaw):
    # msg = oscbuildparse.OSCMessage("/drogni/"+str(droneID)+"/rot", None, [roll, pitch, yaw])
    # rot = oscbuildparse.OSCMessage("/drogni/drone"+str(droneID)+"_rot_x", ",f", [roll])
    # msg = oscbuildparse.OSCMessage("/test/me", ",sif", ["roll", roll, roll])
    # osc_send(rot, "drognoBack")
    print (roll, pitch, yaw)

    rotX = oscbuildparse.OSCMessage("/drogni/drone"+str(droneID)+"_rot_x", ",f", [roll])
    rotY = oscbuildparse.OSCMessage("/drogni/drone"+str(droneID)+"_rot_y", ",f", [pitch])
    rotZ = oscbuildparse.OSCMessage("/drogni/drone"+str(droneID)+"_rot_z", ",f", [yaw])
    rot = oscbuildparse.OSCBundle(oscbuildparse.OSC_IMMEDIATELY, [rotX,rotY,rotZ])
    osc_send(rot, "drognoBack")



def sendPose(droneID, x, y, z):
    pos = oscbuildparse.OSCMessage("/drogni/drone_"+str(droneID)+"_pos_x",",f", x)
    # pos = oscbuildparse.OSCMessage("/drogni/"+str(droneID)+"/pose", ",f", [x, y, z])
    osc_send(pos, "drognoBack") 
    print (x, y, z)


# sendRotation(1,10,20,30)
# sendPose(1,1,0,1)

