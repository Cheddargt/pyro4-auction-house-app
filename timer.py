# import the time module
import time
import threading
  
# define the countdown func.
def countdown(t, callback):
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1
    
    callback()
    return 0
    
def finished():
    return True
      
def start(end_time, callback):
    thread = threading.Thread(target=countdown, args=(end_time,callback))  
    thread.start()
    thread.join()
    print("Thread execution completed")