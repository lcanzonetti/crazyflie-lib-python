
import threading
from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder
from pythonosc import osc_server
from pythonosc import dispatcher
from pythonosc import udp_client
from random import uniform

sendingIP     = "192.168.10.255"
sendingPort   = 9201
receivingPort = 9200

print("Starting Client")
client = udp_client.SimpleUDPClient(sendingIP, sendingPort)
testClient = udp_client.SimpleUDPClient(sendingIP, 9200)
print('osc initalized on', sendingIP, sendingPort, receivingPort)


def printCoordinates(unused_addr, args, x,y,z):
    print (unused_addr, args, x,y,z)
# listen to addresses and print changes in values 
dispatcher = dispatcher.Dispatcher()
dispatcher.map("/drogni/", print)



def receiveNewTarget(id,x,y,z,yaw, speed):
    print('dico al drone [%s] di andare a [%s] [%s] [%s], rivolgendosi a [%s], con velocità [%s]', id,x,y,z,yaw, speed )

def start_server(ip, port):
    print("Starting Receiving Server")
    server = osc_server.ThreadingOSCUDPServer( (ip, port), dispatcher)
    print("Serving on {}".format(server.server_address))
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
 
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




 

  