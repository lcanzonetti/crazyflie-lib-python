
import threading
from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder
from pythonosc import osc_server
from pythonosc import dispatcher
from pythonosc import udp_client
from random import uniform
import repeatedTimer as rp

sendingIP     = "192.168.10.255"
sendingPort   = 9201
receivingPort = 9200

drogni = {}
isSendEnabled = True

client           = udp_client.SimpleUDPClient(sendingIP, sendingPort)
companionclient  = udp_client.SimpleUDPClient(sendingIP, 12321)
print('osc initalized on', sendingIP, sendingPort)
 
def setSendEnabled(unused_addr, args, isEnabled):
    isSendEnabled = isEnabled
    print('me dici:')
    print(unused_addr, args, isEnabled)
def getSendEnabled():
    return isSendEnabled
def comè(uno): # è booleano oppure no?
    uno = uno *1
    return uno
def updateCompanion():
    def daje ():
        if not isSendEnabled:
            companionclient.send_message("/style/bgcolor/10/5", [10, 235, 10])
            companionclient.send_message("/style/text/10/5",  "non mando")
        else:
            companionclient.send_message("/style/bgcolor/10/5", [235, 10, 10])
            companionclient.send_message("/style/text/10/5",  "mando")

      # start timer
    timer = rp.RepeatedTimer(1, daje)
    # Press button 5 on page 1 down and hold
updateCompanion()
 
###########################  whole swarm
def takeoff(unused_addr, args, isEnabled):
    print(unused_addr, args, isEnabled)
    if not isEnabled:
        print('chief says we\'re gonna take the fuck off')
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].takeoff(0.45, 2.45)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def go(unused_addr, args, isEnabled):
    if not isEnabled:
        print('chief says we\'re gonna do shit at sequence %s' % args)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].go(args)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def goTo     (unused_addr,robba, x,y,z ):
    if isSendEnabled:
        print('uh, say they want we\'re gonna go at position %s %s %s' % (x,y,z))

        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goTo(x,y,z)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def goLeft   (unused_addr,yo, quanto):
    if isSendEnabled:
        print('chief says we\'re gonna go leftwards by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goLeft(quanto)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def goRight  (unused_addr, yo, quanto):
    if isSendEnabled:
        print('chief says we\'re gonna go rightwards by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goRight(quanto)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def goForward(unused_addr, yo, quanto):
    if isSendEnabled:
        print('chief says we\'re gonna go forward by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goForward(quanto)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def goBack   (unused_addr, yo, quanto):
    if isSendEnabled:
        print('chief says we\'re gonna go back by %s ' % quanto)
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goBack(quanto)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def land     (unused_addr, args, quanto):
    if not isSendEnabled:
        print('chief says we\'re gotta be grounded')
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].land(quanto)
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def home     (unused_addr, args):
     if isSendEnabled:
        print('chief says we\'re gonna go home')
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].goToHome()
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def ringColor(unused_addr, *args):
     if isSendEnabled:
        # print('how fancy would it be to all look %s?' % args )
        print (args[2])
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].setRingColor(args[0], args[1], args[2])
                # drogni[drogno].alternativeSetRingColor(args)

            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
def kill     (unused_addr, *args):
     if isSendEnabled:
        print('everybody fuck now' % args )
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].killMeHardly()
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)
###########################  single fella

def receiveNewTarget(id,x,y,z,yaw, speed, r,g,b):
    print('dico al drone [%s] di andare a [%s] [%s] [%s], rivolgendosi a [%s], con velocità [%s]', id,x,y,z,yaw, speed )

def printCoordinates(unused_addr, args, x,y,z, ID):
    print ('il drone %s dovrebbe andare a %s %s %s' %( ID, x,y,z))

    if isSendEnabled:
        mandacelo(ID, x, y, z)
    else:
        print('ma i comandi di movimento disabilitati')

def mandacelo(ID, x, y, z):
    try:
        drogni[ID].goTo(x,y,z)
    except:
        print('il drogno %s è scollegato' % ID)



###########################  OSC routing
dispatcher = dispatcher.Dispatcher()
dispatcher.map("/companion/isSendEnabled", setSendEnabled, 'companion')
###########################  whole swarm routing
dispatcher.map("/takeoff",   takeoff, 'yo')
dispatcher.map("/start",     go,      'yo')
dispatcher.map("/land",      land,    'yo')
dispatcher.map("/home",      home,    'yo')
dispatcher.map("/goTo",      goTo,    'yo')
dispatcher.map("/goLeft",    goLeft,  'yo')
dispatcher.map("/goRight",   goRight, 'yo')
dispatcher.map("/goForward", goForward,'yo')
dispatcher.map("/goBack",    goBack,   'yo')
dispatcher.map("/ringColor", ringColor)

###########################  single fella
dispatcher.map("/d3/drone/pos", printCoordinates, 'pos')
dispatcher.map("/d3/drone/rot", printCoordinates, 'rot')
dispatcher.map("/notch/drone*/yaw",   printCoordinates, 'rot')
dispatcher.map("/notch/drone*/color", printCoordinates, 'rot')
dispatcher.map("/notch/drone*/pos",   printCoordinates, 'rot')















def ping():
    print('pong')
    print(drogni)









def start_server():
    print("Starting OSC Receiving Server")
    server = osc_server.ThreadingOSCUDPServer( ('0.0.0.0', receivingPort), dispatcher)
    print("Server OSC partito {}".format(server.server_address))
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
start_server()
# ################ feedbacksssssssss
# 
#  
def sendRotation(droneID, yaw):
# def sendRotation(droneID, roll, pitch, yaw):
    # client.send_message("/drogni/drone"+str(droneID)+"_rot_x", roll)
    # client.send_message("/drogni/drone"+str(droneID)+"_rot_y", pitch)
    client.send_message("/drogni/drone"+str(droneID)+"_rot_z", yaw)
    # print (droneID, roll, pitch, yaw)
    # print (droneID, yaw)

def sendPose(droneID, x, y, z):
    client.send_message("/drogni/drone"+str(droneID)+"_pos_x", x)
    client.send_message("/drogni/drone"+str(droneID)+"_pos_y", y)
    client.send_message("/drogni/drone"+str(droneID)+"_pos_z", z)
    # client.send_message("/drogni/t/", uniform(2.5, 10.0)  )
    # print (x, y, z)




 

  