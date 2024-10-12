
"""
   Prints temperature on request.
   example1.py should be set running from another
   command prompt.
"""

import sys

sys.path.insert(0, "/home/bernard/git/indipyclient")


import threading, collections

from indipyclient.queclient import runqueclient

# create two queues

# rxque giving received data
rxque = collections.deque(maxlen=1)

# length of one so old measurements are bumped off
# and rxque[0] is always the latest.

# txque transmit data
txque = collections.deque()

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
            # get latest data received on queue
            rxitem = rxque.popleft()
            tempvector = rxitem.snapshot["Thermostat"]["temperaturevector"]
            tempstr = tempvector.getformattedvalue("temperature")
        except (IndexError, KeyError):
            print("Waiting")
            continue
        if rxitem.timestamp:
            # get local time
            timestr = rxitem.timestamp.astimezone(tz=None).strftime('%H:%M:%S')
        else:
            timestr = "No timestamp"
        print(f"{timestr} Temperature: {tempstr}")

    elif value == "q" or value == "Q":
        break

# When the loop ends, transmit a None value to shut down the queclient
txque.append(None)
# and wait for the clientthread to stop
clientthread.join()
