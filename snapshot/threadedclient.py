# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipyclient",
# ]
# ///

import asyncio, collections, threading, time

from indipyclient.queclient import QueClient



# a blocking function to be run in a thread

def numberdoubler(myclient, txque, rxque):
    """get item from rxque, manipulate it, and send a value
       back to the driver in txque.
       as a test, make this blocking and run it in a thread"""
    try:
        while not myclient.stop:
            # this loop stops when myclient stops
            try:
                event = rxque.popleft()
            except IndexError:
                time.sleep(0.1)
                continue
            if event.devicename != 'Counter' or event.vectorname != 'txcount':
                continue
            if 'txvalue' not in event.snapshot['Counter']['txcount']:
                continue
            # get the value sent by the driver
            value = float(event.snapshot['Counter']['txcount']['txvalue'])
            # manipulate it, in this example just multiply by two
            # and transmit manipulated value back in vector rxvector
            txque.append( ('Counter', 'rxvector',  {'rxvalue':value * 2}) )
    finally:
        # if this stops, shutdown myclient
        txque.append(None)


if __name__ == "__main__":

    # create queue where updated data will be transmitted
    txque = collections.deque()
    # create queue where client will put events
    rxque = collections.deque()
    # create a QueClient object
    myclient = QueClient(txque,rxque)

    # run numberdoubler in its own thread
    doubler = threading.Thread(target=numberdoubler, args=(myclient, txque, rxque))
    doubler.start()
    print(f"Running {__file__}")
    # run myclient.asyncrun()
    asyncio.run(myclient.asyncrun())
    # and wait for the doubler thread to stop
    doubler.join()
