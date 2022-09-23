
from OSC_feedabcker import CompanionFeedbacco
import multiprocessing
import threading
import time
from threading import Lock
from multiprocessing.connection import Client
from multiprocessing.connection import Listener
from multiprocessing import Process, Queue, Event
from osc4py3.as_eventloop import *
from osc4py3 import oscmethod as osm
from osc4py3 import oscbuildparse

################################################  companion feedback via OSC:
COMPANION_FEEDBACK_SENDINGPORT = 12321
companionFeedbackCue           = Queue()
COMPANION_FEEDBACK_IP          = None
COMPANION_PAGES                = ['92', '93', '94']
TC_COMPANION_PAGE              = '91'
SWARM_PAGE                     = '90'
COMPANION_ENABLE_BUTTON        = '25'
COMPANION_UPDATE_RATE          = 2
COMPANION_FEEDBACK_ENABLED     = True
GLOBAL_FREQUENCY               = 0.9
finished                       = False
can_we_fly                     = False
can_we_send                    = False
drogni                         = {}

def startCompanionFeedback():
    if COMPANION_FEEDBACK_ENABLED:
        companionFeedbackerInstance = CompanionFeedbacco(companionFeedbackCue, COMPANION_FEEDBACK_IP, COMPANION_FEEDBACK_SENDINGPORT)
        companionFeedbackProcess = Process(target=companionFeedbackerInstance.start)
        companionFeedbackProcess.daemon = True
        companionFeedbackProcess.start()


def setCompanionRate(address, args):
    global COMPANION_UPDATE_RATE
    # print(args)
    if args[0] == '+':
        COMPANION_UPDATE_RATE += 0.1
    elif args[0] == '-':
        if COMPANION_UPDATE_RATE > 0:
            COMPANION_UPDATE_RATE -= 0.1
    COMPANION_UPDATE_RATE = round(COMPANION_UPDATE_RATE, 2)
    print(COMPANION_UPDATE_RATE)

def resetCompanion():
    if COMPANION_FEEDBACK_ENABLED:
        swarmTakeOff = oscbuildparse.OSCMessage("/style/text/"+SWARM_PAGE+"/2",    None,   ['TAKE OFF'])
        swarmTakeOff_bkgcol = oscbuildparse.OSCMessage("/style/bgcolor/"+SWARM_PAGE+"/2", ",iii",   [20, 20, 20])
        swarmTakeOff_col = oscbuildparse.OSCMessage("/style/color/"+SWARM_PAGE+"/2",   ",iii",   [100, 100, 100])
        sbirulino = [swarmTakeOff, swarmTakeOff_bkgcol, swarmTakeOff_col]
        companionFeedbackCue.put_nowait(sbirulino)

        for i in range(2, 9):
            j = 0
            for cp in COMPANION_PAGES:
                intst = oscbuildparse.OSCMessage("/style/text/"+cp+"/" + str(i),      None,   ['drone '+str(i-2+(j*7))])
                int_bkgcol = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" + str(i),    ",iii",   [1, 1, 1])
                int_col = oscbuildparse.OSCMessage("/style/color/"+cp+"/" + str(i),    ",iii",   [60, 60, 60])

                status = oscbuildparse.OSCMessage("/style/text/"+cp+"/" + str(i+8),    None,   ['sconnesso'])
                status_bkgcol = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" + str(i+8),  ",iii",   [1, 1, 1])
                status_col = oscbuildparse.OSCMessage("/style/color/"+cp+"/" + str(i+8),  ",iii",   [120, 120, 120])

                tkfland = oscbuildparse.OSCMessage("/style/text/"+cp+"/" + str(i+16),   None,   ['take off'])
                tkfland_bkg = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" + str(i+16), ",iii",   [60,  20,   1])
                tkfland_col = oscbuildparse.OSCMessage("/style/color/"+cp+"/" + str(i+16), ",iii",   [60, 60, 60])

                engage = oscbuildparse.OSCMessage("/style/text/"+cp+"/" + str(i+24),   None,   ['engage'])
                engage_bkg = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" + str(i+24), ",iii",   [10, 80, 10])
                engage_col = oscbuildparse.OSCMessage("/style/color/"+cp+"/" + str(i+24), ",iii",   [255, 255, 255])

                bandoleon = [intst, int_bkgcol, int_col, status, status_bkgcol, status_col,
                             tkfland, tkfland_bkg, tkfland_col, engage, engage_bkg, engage_col]
                companionFeedbackCue.put_nowait(bandoleon)
                j += 1


def updateCompanion():
    global bufferone
 
    def daje():
        print("Update di companion partito.")

        takeOffOrLandText = 'take off'
        takeOffOrLandColor = [200, 20, 40]
        engageText = 'not engaged'
        engageColor = [20, 240, 80]
        swarmTakeOff_color = [20, 20, 20]

        while not finished:
            if COMPANION_FEEDBACK_ENABLED:
                infinitaRoba = []
                time.sleep(COMPANION_UPDATE_RATE)
                # listaTimecode    = timecode.split(':')
                # timecode_hours   = oscbuildparse.OSCMessage("/style/text/"+TC_COMPANION_PAGE+"/"    + str(29),   None,   [listaTimecode[0]])
                # timecode_minutes = oscbuildparse.OSCMessage("/style/text/"+TC_COMPANION_PAGE+"/"    + str(30),   None,   [listaTimecode[1]])
                # timecode_seconds = oscbuildparse.OSCMessage("/style/text/"+TC_COMPANION_PAGE+"/"    + str(31),   None,   [listaTimecode[2]])
                # timecode_frames  = oscbuildparse.OSCMessage("/style/text/"+TC_COMPANION_PAGE+"/"    + str(32),   None,   [listaTimecode[3]])
                timecode_hours = oscbuildparse.OSCMessage(
                    "/style/text/"+TC_COMPANION_PAGE+"/" + str(29),   None,   ['00:'])
                timecode_minutes = oscbuildparse.OSCMessage(
                    "/style/text/"+TC_COMPANION_PAGE+"/" + str(30),   None,   ['00:'])
                timecode_seconds = oscbuildparse.OSCMessage(
                    "/style/text/"+TC_COMPANION_PAGE+"/" + str(31),   None,   ['00:'])
                timecode_frames = oscbuildparse.OSCMessage(
                    "/style/text/"+TC_COMPANION_PAGE+"/" + str(32),   None,   ['00'])
                companionRate = oscbuildparse.OSCMessage(
                    "/style/text/"+TC_COMPANION_PAGE+"/" + str(11),   None,   [str(COMPANION_UPDATE_RATE)])
                commandsRate = oscbuildparse.OSCMessage(
                    "/style/text/"+TC_COMPANION_PAGE+"/" + str(13),   None,   [str(GLOBAL_FREQUENCY)])
                infinitaRoba = [timecode_hours, timecode_minutes,
                                timecode_seconds, timecode_frames, companionRate, commandsRate]

                if can_we_fly:
                    swarmTakeOff_color = [20, 255, 60]
                else:
                    swarmTakeOff_color = [60, 60, 60]

                sbc = oscbuildparse.OSCMessage("/style/bgcolor/"+SWARM_PAGE+"/2", ",iii", swarmTakeOff_color)
                infinitaRoba.extend([sbc])

                if not weMaySend:  # *******************  SEND ENABLING
                    for cp in COMPANION_PAGES:
                        col = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" +
                                                       COMPANION_ENABLE_BUTTON, None,  [10, 235, 10])
                        txt = oscbuildparse.OSCMessage("/style/text/"+cp+"/" +
                                                       COMPANION_ENABLE_BUTTON, None,   ["non ricevo"])
                        col2 = oscbuildparse.OSCMessage("/style/bgcolor/90/21", None,   [10, 235, 10])
                        txt2 = oscbuildparse.OSCMessage("/style/text/90/21",    None,   ["non ricevo"])
                        infinitaRoba.extend([col, txt, col2, txt2])
                else:
                    for cp in COMPANION_PAGES:
                        col = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" +
                                                       COMPANION_ENABLE_BUTTON, None,  [235, 10, 10])
                        txt = oscbuildparse.OSCMessage("/style/text/"+cp+"/" +
                                                       COMPANION_ENABLE_BUTTON, None,   ["ricevo"])
                        col2 = oscbuildparse.OSCMessage("/style/bgcolor/90/21", None,   [235, 10, 10])
                        txt2 = oscbuildparse.OSCMessage("/style/text/90/21", None,   ["ricevo"])
                        infinitaRoba.extend([col, txt, col2, txt2])

                for drogno in drogni:  # *******************  singol-drogn
                    cp = COMPANION_PAGES[0]
                    iddio = drogni[drogno].ID
                    d = drogni[drogno]
                    if iddio >= 7 and iddio < 14:
                        cp = int(cp) + 1
                        iddio -= 7
                    if iddio >= 14:
                        cp = int(cp) + 2
                        iddio -= 14
                    cp = str(cp)

                    if d.isReadyToFly:
                        takeOffOrLandColor = [20, 200, 40]
                    else:
                        takeOffOrLandColor = [100, 90, 40]

                    if d.isFlying:
                        takeOffOrLandText = 'land'
                    else:
                        takeOffOrLandText = 'take off'

                    if d.isEngaged:
                        engageText = 'engaged'
                        engageColor = [240, 20, 80]
                    else:
                        engageText = 'not engaged'
                        engageColor = [20, 240, 80]

                    rgb = [drogni[drogno].requested_R, drogni[drogno].requested_G, drogni[drogno].requested_B]
                    if not any(rgb):
                        rgb = [40, 40, 40]
                    if d.standBy:
                        rgb = [10, 30, 10]

                    int_bkgcol = oscbuildparse.OSCMessage("/style/bgcolor/"+cp+"/" + str(iddio+2),    ",iii", rgb)
                    int_col = oscbuildparse.OSCMessage(
                        "/style/color/"+cp+"/" + str(iddio+2),    ",iii",   [255, 255, 255])

                    status = oscbuildparse.OSCMessage("/style/text/"+cp+"/" + str(iddio+2+8),
                                                      ",s",   [d.statoDiVolo + ' ' + d.batteryVoltage])
                    status_bkgcol = oscbuildparse.OSCMessage(
                        "/style/bgcolor/"+cp+"/" + str(iddio+2+8),  ",iii",   [1, 1, 1])
                    status_col = oscbuildparse.OSCMessage(
                        "/style/color/"+cp+"/" + str(iddio+2+8),  ",iii",   [255, 255, 255])

                    tkfland = oscbuildparse.OSCMessage(
                        "/style/text/"+cp+"/" + str(iddio+2+16),   None,   [takeOffOrLandText])
                    tkfland_bkg = oscbuildparse.OSCMessage(
                        "/style/bgcolor/"+cp+"/" + str(iddio+2+16), ",iii",   takeOffOrLandColor)
                    tkfland_col = oscbuildparse.OSCMessage(
                        "/style/color/"+cp+"/" + str(iddio+2+16), ",iii",   [40, 40, 40])

                    engage = oscbuildparse.OSCMessage("/style/text/"+cp+"/" + str(iddio+2+24),   None, [engageText])
                    engage_bkg = oscbuildparse.OSCMessage(
                        "/style/bgcolor/"+cp+"/" + str(iddio+2+24), ",iii", engageColor)
                    engage_col = oscbuildparse.OSCMessage(
                        "/style/color/"+cp+"/" + str(iddio+2+24), ",iii", [255, 255, 255])

                    infinitaRoba.extend([int_bkgcol, int_col, status, status_bkgcol, status_col,
                                        tkfland, tkfland_bkg, tkfland_col, engage, engage_bkg, engage_col])
                    companionFeedbackCue.put_nowait(infinitaRoba)
    nnamo = threading.Thread(target=daje).start()


def weMaySend(yes_or_no):
    global weMaySend
    weMaySend = yes_or_no

def setFlyability(si_o_no):
    global can_we_fly 
    can_we_fly = si_o_no

def set_command_frequency(freq):
    global GLOBAL_FREQUENCY
    GLOBAL_FREQUENCY = freq

def ends_it_when_it_needs_to_end():
    global finished
    companionFeedbackCue.put('fuck you')
    finished = True
