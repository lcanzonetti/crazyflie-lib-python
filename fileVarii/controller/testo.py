import multiprocessing
import random
from multiprocessing import Process, Queue
import time
import sys
import pytimecode
import finestrina
import threading
from threading import Thread


def reader_proc(queue):
    ## Read from the queue; this will be spawned as a separate Process
    while True:
        msg = queue.get()         # Read from the queue and do nothing
        if (msg == 'DONE'):
            break

def writer(count, queue):
    ## Write to the queue
    for ii in range(0, count):
        queue.put(ii)             # Write 'count' numbers into the queue
    queue.put('DONE')

if __name__=='__main__':
    
    # pino = {'carlo': [1,2,3], 'pincherlo': [4,5,6]}
    # if 'carlo' in pino:
    #     print( pino['carlo'])
    # pqueue = Queue() # writer() writes to pqueue from _this_ process
    # for count in [10**3, 10**4, 10**5]:             
    #     ### reader_proc() reads from pqueue as a separate process
    #     reader_p = Process(target=reader_proc, args=((pqueue),))
    #     reader_p.daemon = True
    #     reader_p.start()        # Launch reader_proc() as a separate python process

    #     _start = time.time()
    #     writer(count, pqueue)    # Send a lot of stuff to reader()
    #     reader_p.join()         # Wait for the reader to finish
    #     print("Sending {0} numbers to Queue() took {1} seconds".format(count, 
    #         (time.time() - _start)))
    timecode = "00:00:00:00"
    pino = pytimecode.PyTimeCode(framerate=25,frames=0, iter_return="frames")
  
    for i in range(100):
        print(pino.next())