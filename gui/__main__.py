
import asyncio, queue, threading

import sys
sys.path.insert(0, "/home/bernie/git/indipyclient")

from indipyclient.queclient import runqueclient

from .guiclient import rungui



if __name__ == "__main__":

    # create two queues
    # rxque giving received data
    rxque = queue.Queue(maxsize=4)
    # txque transmit data
    txque = queue.Queue(maxsize=4)


    # run the client in its own thread
    clientapp = threading.Thread(target=runqueclient, args=(txque, rxque))
    clientapp.start()
    # run the gui in this thread
    print(f"Running {__file__}")
    rungui(txque, rxque)
    # and wait for the clientapp thread to stop
    clientapp.join()
