
import threading
import time
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
bufferone = {}
isSendEnabled = False
finished = True

# client           = udp_client.SimpleUDPClient(sendingIP, sendingPort)
# companionclient  = udp_client.SimpleUDPClient(sendingIP, 12321)

# Import needed modules from osc4py3
from osc4py3.as_eventloop import *
from osc4py3 import oscmethod as osm

  
def setSendEnabled (*args):
    global isSendEnabled
    isSendEnabled = not isSendEnabled
    
    print('me dici: %s' % isSendEnabled)
    updateCompanion()
def getSendEnabled(self):
    return self.isSendEnabled
def comè(uno): # è booleano oppure no?
    uno = uno *1
    return uno
def updateCompanion():
    def daje ():
        pass
        # if not isSendEnabled:
        #     companionclient.send_message("/style/bgcolor/91/21", [10, 235, 10])
        #     companionclient.send_message("/style/text/91/21",  "non mando")
        # else:
        #     companionclient.send_message("/style/bgcolor/91/21", [235, 10, 10])
        #     companionclient.send_message("/style/text/91/21",  "mando")

      # start timer
    # timer = rp.RepeatedTimer(1, daje)
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
    if isSendEnabled:
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
        print('how fancy would it be to all look %s?' % [args] )
        # print (args[2])
        for drogno in drogni:
            drogni[drogno].setRingColor(args[1], args[2], args[3])
            # drogni[drogno].alternativeSetRingColor(args)
 
def kill     (unused_addr, *args):
     if isSendEnabled:
        print('everybody fuck now' % args )
        for drogno in drogni:
            if drogni[drogno].is_connected:
                drogni[drogno].killMeHardly()
            else:
                print('il drogno %s non è connesso' % drogni[drogno].name)

###########################  single fella


def printAndSendCoordinates():
    time.sleep(5)
    while True:
        time.sleep(0.5)
        for drogno in drogni:
            iddio = drogni[drogno].ID
            print ('il drone %s dovrebbe andare a %s %s %s' %( bufferDrone[drogni[drogno].ID].name, bufferDrone[iddio].requested_X,bufferDrone[iddio].requested_Y,bufferDrone[iddio].requested_Z))
            if isSendEnabled:
                drogni[drogno].
                drogni[drogno].vacce()
            else:
                # print('ma i comandi di movimento disabilitati')
                pass

 


###########################  OSC routing
# dispatcher = dispatcher.Dispatcher()
# dispatcher.map("/companion/isSendEnabled", setSendEnabled, 'companion')
# ###########################  whole swarm routing
# dispatcher.map("/takeoff",   takeoff, 'yo')
# dispatcher.map("/start",     go,      'yo')
# dispatcher.map("/land",      land,    'yo')
# dispatcher.map("/home",      home)
# dispatcher.map("/goTo",      goTo,    'yo')
# dispatcher.map("/goLeft",    goLeft,  'yo')
# dispatcher.map("/goRight",   goRight, 'yo')
# dispatcher.map("/goForward", goForward,'yo')
# dispatcher.map("/goBack",    goBack,   'yo')
# dispatcher.map("/ringColor", ringColor, 'culo demoniaco')

###########################  single fella
# dispatcher.map("/d3/drone/pos",  , 'pos')
# dispatcher.map("/d3/drone/rot",  , 'rot')
# dispatcher.map("/notch/drone*/X",   setRequested,  'yeah')
# dispatcher.map("/notch/drone*/Y",   setRequested,  'yeah')
# dispatcher.map("/notch/drone*/Z",   setRequested,  'yeah')
# dispatcher.map("/notch/drone*/R",   setRequested,  'yeah')
# dispatcher.map("/notch/drone*/G",   setRequested,  'yeah')
# dispatcher.map("/notch/drone*/B",   setRequested,  'yeah')

def setRequested(*args):
    iddio     = int(args[0].split('/')[2][-1])
    parametro = args[0][-1]
    value     = round(args[1],3)

    # print (iddio, parametro, value)
    # try:
    if parametro == 'X' or parametro == 'Y':
        if value < -2:
            value = -2
        if value > 2:
            value = 2
    if parametro == 'Z':
        if value < 0.3:
            value = 0.30
    
    bufferDrone[iddio].__dict__[f'requested_{parametro}'] = value
    # print('provo a variare il parametro %s mettendoci %s' % (parametro, value))
    # except:
    #     print('qualche porchiddio')


def start_server():
    print("Starting OSC Receiving Server")
    # server = osc_server.ThreadingOSCUDPServer( ('0.0.0.0', receivingPort), dispatcher)
    # print("Server OSC partito {}".format(server.server_address))
    # thread = threading.Thread(target=server.serve_forever, daemon=True).start()
    # ################ init

    # Periodically call osc4py3 processing method in your event loop.
    # Start the system.
    osc_startup()

    # Make server channels to receive packets.
    # osc_udp_server("192.168.0.0", 3721, "aservername")
    osc_udp_server("0.0.0.0", receivingPort, "anotherserver")
    print('osc initalized on', sendingIP, sendingPort)

    osc_method("/notch/drone*/X",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/notch/drone*/X",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/notch/drone*/Y",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/notch/drone*/Z",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/notch/drone*/R",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/notch/drone*/G",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/notch/drone*/B",   setRequested, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/companion/isSendEnabled", setSendEnabled, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    ###########################  whole swarm routing
    osc_method("/takeoff",   takeoff, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/start",     go,      argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/land",      land,    argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/home",      home,    argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goTo",      goTo,    argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goLeft",    goLeft,  argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goRight",   goRight, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goForward", goForward, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/goBack",    goBack,    argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    osc_method("/ringColor", ringColor, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)
    global finished 
    finished = False
    while not finished:
        # …
        osc_process()
        # …

    # Properly close the system.
    # osc_terminate()
if __name__ == '__main__':
    OSCRefreshThread = threading.Thread(target=start_server,daemon=True).start()
    OSCRefreshThread = threading.Thread(target=printAndSendCoordinates,daemon=True).start()
    while True:
        pass




def faiIlBufferon():
    for i in range (1,20):
        bufferone[i] = bufferDrone(i)
    # print ('bufferon')  
    # print (bufferone)


class bufferDrone():
    def __init__(self, ID, ):
        self.ID          = int(ID)
        self.name        = 'bufferDrone'+str(ID)
        
        self.requested_X            = 0.0
        self.requested_Y            = 0.0
        self.requested_Z            = 0.0
        self.requested_R            = 0.0
        self.requested_G            = 0.0
        self.requested_B            = 0.0
        self.yaw                   = 0.0


 

# ################ feedbacksssssssss
# 
#  
def sendRotation(droneID, yaw):
    pass
    # client.send_message("/drogni/drone"+str(droneID)+"_rot_x", roll)
    # client.send_message("/drogni/drone"+str(droneID)+"_rot_y", pitch)
    # client.send_message("/drogni/drone"+str(droneID)+"_rot_z", yaw)
    # print (droneID, roll, pitch, yaw)
    # print (droneID, yaw)

def sendPose(droneID, x, y, z):
    pass
    # client.send_message("/drogni/drone"+str(droneID)+"_pos_x", x)
    # client.send_message("/drogni/drone"+str(droneID)+"_pos_y", y)
    # client.send_message("/drogni/drone"+str(droneID)+"_pos_z", z)
    # client.send_message("/drogni/t/", uniform(2.5, 10.0)  )
    # print (x, y, z)




 

  