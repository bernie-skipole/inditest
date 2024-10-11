
"""
   Prints temperature on request.
   example1.py should be set running from another
   command prompt.
"""


import queue, threading, collections

from indipyclient.queclient import runqueclient

# create two queues

# rxque giving received data
rxque = collections.deque(maxlen=1)

# txque transmit data
txque = queue.Queue(maxsize=4)

# run the queclient in its own thread
clientthread = threading.Thread(target=runqueclient, args=(txque, rxque))

# The args argument could also have hostname and port specified
# if the Thermostat server is running elsewhere
clientthread.start()

txque.append("snapshot")
print("Input a T for temperature, or Q for Quit")
while True:
    value = input("T or Q:")
    if value == "t" or value == "T":
        try:
            # get latest data received
            rxitem = rxque[0]
        except IndexError:
            print("Nothing received yet")
            continue
        temperature = rxitem.snapshot["Thermostat"]["temperaturevector"]["temperature"]
        timestamp = rxitem.timestamp.isoformat(sep='T')
        print(f"{timestamp} Temperature: {timestamp}")
    elif value == "q" or value == "Q":
        break

# When the loop ends, transmit a None value to shut down the queclient
txque.put(None)
# and wait for the clientthread to stop
clientthread.join()
