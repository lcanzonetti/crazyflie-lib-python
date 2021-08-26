from threading import Thread
import threading
import time
import random
import OSCStuff as OSC
import timerino as myTimer

exitFlag = 0
treddi = []


class Drogno (threading.Thread):
    def __init__(self, ID, name, counter):
      threading.Thread.__init__(self)
      self.ID = ID
      self.name = name
      self.counter = counter
      self.statoDiVolo = 'idle'
      self.durataVolo = random.randint(1,4)
      self.exitFlag = 0
      self.controlThread         = False
      self.printThread           = False
      self.currentSequenceThread = False
      self.exitingTimer          = False
      self.idleExitTime          = 10

    def run(self):
      print ("Starting " + self.name)
      self.controlThread = threading.Thread(target=self.controlThreadRoutine).start()
      self.printThread   = threading.Thread(target=self.printStatuse).start()
      print ("Exiting " + self.name)
    #   t.join()

    def printStatus(self, threadName, counter, delay):
        while not self.exitFlag:
            time.sleep(delay)
            print ("%s: %s" % (threadName, self.statoDiVolo))
            # print ("%s: %s : %s" % (threadName, time.ctime(time.time()), self.statoDiVolo))
    
    def controlThreadRoutine(self):
        while not self.exitFlag:
            if (self.statoDiVolo == 'esecuzione sequenza!'):
                self.sequenzaDiVolo()
                if self.exitingTimer != False:
                    self.exitingTimer.stop()
                    self.exitFlag = 0

            elif (self.statoDiVolo == 'landing'):
                time.sleep(2)
                self.statoDiVolo = 'idle'
                def exit():
                    print('exitFlag is now set, bye kiddo\n')       
                    self.exitFlag = 1
                # self.exitingTimer = myTimer.Timer(self.idleExitTime, exit).start()
                # print (self.exitingTimer)
                # print('exiting in 5 seconds') 
                

    def sequenzaDiVoloSimulata(self):     
        def volo():
            print('il drone %s vola! e volerà per %s secondi' % (self.ID, self.durataVolo))
            time.sleep(self.durataVolo)
            self.statoDiVolo = 'finito sequenza'
            # self.currentSequenceThread.join()

        if not self.currentSequenceThread:
            self.currentSequenceThread = threading.Thread(target=volo)
            self.currentSequenceThread.start()
            print('start!')
        # else:
            # print ('il thread di volo è già iniziato_______')

    def takeoff(self):
        self.statoDiVolo = 'decollato!'

    def go(self):
        if self.statoDiVolo == 'decollato!' or self.statoDiVolo == 'finito sequenza':
            self.statoDiVolo = 'esecuzione sequenza!'
        else:
            print('not ready!')

    def land(self):
        self.statoDiVolo = 'landing'
        



# Create new threads

for i in range(9):
    treddi.append(Drogno(i, "drogno"+str(i), 1))
    treddi[i].start()
    OSC.drogni = treddi

# OSC.ping()


finito = False
while True:
    time.sleep(5)
    if not finito: 
        # for i in range(len(treddi)):
        #     treddi[i].statoDiVolo = 'decollato!'
        # finito = True
        pass
    else:
        # Wait for all threads to complete
        for t in treddi:
            t.join()
            print ("Exiting Main Thread")
            exit()

    # pass


# Start new Threads

print ("Exiting Main Thread")