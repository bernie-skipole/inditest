
"""sendblob.py should be run in another terminal

Saves received blobs in folder ./ and if P pressed
it prints the last filename received
"""

import collections, threading, time

# import the function runqueclient which can
# be run in a thread to operate a QueClient

from indipyclient.queclient import runqueclient


if __name__ == "__main__":

    # create two queues
    rxque = collections.deque(maxlen=1)
    txque = collections.deque()

    # run the queclient in its own thread, with blobfolder set as "./"
    clientthread = threading.Thread(target=runqueclient, args=(txque, rxque, "localhost", 7624, "./"))
    clientthread.start()

    txque.append("snapshot")

    # wait for connection
    while True:
        if rxque:
            snapshot = rxque[0].snapshot
            if snapshot.connected:
                break
        time.sleep(0.5)

    # send an enable blob request
    txque.append(("blobmaker", "blobvector",  "Also"))

    print("Input a P for print last filename, or Q for Quit")
    while True:
        value = input("P or Q:")
        if value == "p" or value == "P":
            try:
                # get latest data received on queue
                rxitem = rxque[0]
                vector = rxitem.snapshot["blobmaker"]["blobvector"]
                filename = vector.member("blobmember").user_string
                if filename:
                    print(filename)
                else:
                    print("Nothing received yet")
            except (IndexError, KeyError):
                print("Waiting")
        elif value == "q" or value == "Q":
            break

    # When the loop ends, transmit a None value to shut down the queclient
    txque.append(None)
    # and wait for the clientthread to stop
    clientthread.join()
