from threading import Thread
import threading
import time
import random
import OSCStuff as OSC

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
      self.currentSequenceThread = False

    def run(self):
      print ("Starting " + self.name)
      t = threading.Thread(target=self.checkSequenzaDiVolo).start()
      self.print_time(self.name, 5, self.counter)      
      print ("Exiting " + self.name)
    #   t.join()

    def print_time(self, threadName, counter, delay):
        while not self.exitFlag:
            time.sleep(delay)
            print ("%s: %s" % (threadName, self.statoDiVolo))
            # print ("%s: %s : %s" % (threadName, time.ctime(time.time()), self.statoDiVolo))
    
    def checkSequenzaDiVolo(self):
        while not self.exitFlag:
            if (self.statoDiVolo == 'esecuzione sequenza!'):
                self.sequenzaDiVolo()
            elif (self.statoDiVolo == 'landing'):
                time.sleep(2)
                self.statoDiVolo = 'idle'
                def exit():       
                    self.exitFlag = 1
                T = threading.Timer(5, exit).start()
                print('exiting in 5 seconds') 
                

    def sequenzaDiVolo(self):
            
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