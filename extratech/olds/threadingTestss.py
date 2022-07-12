from threading import Thread
from threading import Event
import time
   
  
class Connection(Thread):
   
    StopEvent = 0
      
    def __init__(self,args):
        Thread.__init__(self)
        self.StopEvent = args
  
    # The run method is overridden to define 
    # the thread body 
    def run(self):
   
        for i in range(1,10):
            if(self.StopEvent.wait(0)):
                print ("Asked to stop")
                break;
   
            print("The Child Thread sleep count is %d"%(i))
            time.sleep(3)
          
        print ("A Child Thread is exiting")
  
Stop = Event()
Connection = Connection(Stop)           
Connection.start()
print("Main thread is starting to wait for 5 seconds")
   
Connection.join(5) 
print("Main thread says : I cant't wait for more than 5 \
seconds for the child thread;\n Will ask child thread to stop")
   
# ask(signal) the child thread to stop
Stop.set()
   
# wait for the child thread to stop
Connection.join()
   
print("Main thread says : Now I do something else to compensate\
the child thread task and exit")
print("Main thread is exiting")