
import threading
from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder
from pythonosc import osc_server
from pythonosc import dispatcher
from pythonosc import udp_client
from random import uniform

sendingIP     = "192.168.10.101"
sendingPort   = 9201
receivingPort = 9200

svormo = []
isSendEnabled = False


print("Starting Client")
client     = udp_client.SimpleUDPClient(sendingIP, sendingPort)
# testClient = udp_client.SimpleUDPClient(sendingIP, 9200)
print('osc initalized on', sendingIP, sendingPort, receivingPort)


def printCoordinates(unused_addr, args, x,y,z, ID):
    print ('il drone %s dovrebbe andare a %s %s %s' %( ID, x,y,z))
    if isSendEnabled:
        mandacelo(ID, x, y, z)

def mandacelo(ID, x, y, z):
    svormo[ID].goTo(x,y,z)



def tipo(roba):
    print (roba)

# listen to addresses and print changes in values 
dispatcher = dispatcher.Dispatcher()
dispatcher.map("/d3/drone/pos", printCoordinates, 'pos')
dispatcher.map("/d3/drone/rot", printCoordinates, 'rot')

def receiveNewTarget(id,x,y,z,yaw, speed):
    print('dico al drone [%s] di andare a [%s] [%s] [%s], rivolgendosi a [%s], con velocità [%s]', id,x,y,z,yaw, speed )

def start_server():
    print("Starting OSC Receiving Server")
    server = osc_server.ThreadingOSCUDPServer( ('0.0.0.0', receivingPort), dispatcher)
    print("Server OSC partito {}".format(server.server_address))
    thread = threading.Thread(target=server.serve_forever)
    thread.start()

# feedbacksssssssss
# 
#  
def sendRotation(droneID, roll, pitch, yaw):
    client.send_message("/drogni/drone"+str(droneID)+"_rot_x", roll)
    client.send_message("/drogni/drone"+str(droneID)+"_rot_y", pitch)
    client.send_message("/drogni/drone"+str(droneID)+"_rot_z", yaw)
    # print (droneID, roll, pitch, yaw)

def sendPose(droneID, x, y, z):
    client.send_message("/drogni/drone"+str(droneID)+"_pos_x", x)
    client.send_message("/drogni/drone"+str(droneID)+"_pos_y", y)
    client.send_message("/drogni/drone"+str(droneID)+"_pos_z", z)
    # client.send_message("/drogni/t/", uniform(2.5, 10.0)  )
    # print (x, y, z)




 

  