from threading import Thread
import threading
import time

classi = []


class MyDamnClass():

    def __init__(self, iddio):
        self.iddio = iddio
        self.contatore = 0

    
    def starta(self):
        # t = threading.Thread(target=self.conta)
        # t.start()
        # t.join()
        gerlo = int(time.time())
        print(gerlo)
        time.sleep(gerlo)
        start_time = time.time()
        interval = 1
        for i in range(20):
            pino = start_time + (i*interval)
            carlo = time.time()
            minchio = pino - carlo
            print(minchio)
            time.sleep(minchio)
            self.conta()

    def conta(self):
        print ('classe %s dice %s' % (self.iddio, self.contatore))
        self.contatore +=1

       



if __name__ == '__main__':
    for i in range(3):
        classi.append  (MyDamnClass(i))
        t = threading.Thread(target=classi[i].starta).start() 


