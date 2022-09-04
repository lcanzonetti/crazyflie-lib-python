import threading, time

new_motorTestCount = 10
current_motorTestCount = 1


def propeller_test():
    def prop_control_loop():
        while(new_motorTestCount - current_motorTestCount) >= 1:
            print ("sto ancora : %s" % (new_motorTestCount - current_motorTestCount))
            time.sleep(0.3)
        print('completo')
        
    # prop_control_loop()
    threading.Thread(target=prop_control_loop).start()


def faiUnaRoba():
    global new_motorTestCount
    global current_motorTestCount
    for i in range (20):
        current_motorTestCount +=1
        time.sleep(0.01)


propeller_test()
# threading.Thread(target=propeller_test).start()
threading.Thread(target=faiUnaRoba).start()