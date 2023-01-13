from datetime import datetime
import time
import threading

def activeTime():
    while True:
        print(threading.active_count())
        now = datetime.now()
        currentTime = now.strftime("%H:%M:%S")
        print(currentTime)
        time.sleep(1)

t1 = threading.Thread(target = activeTime)
t1.start()
