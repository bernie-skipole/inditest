# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipyclient",
# ]
# ///

import asyncio, collections, threading, time

from indipyclient.queclient import runqueclient



def numberdoubler(txque, rxque):
    """get item from rxque, manipulate it, and send a value
       back to the driver in txque. Use CTRL-C to stop"""
    while True:
        try:
            event = rxque.popleft()
        except IndexError:
            time.sleep(0.1)
            continue
        print(event.eventtype)
        if event.devicename != 'Counter' or event.vectorname != 'txcount':
            continue
        try:
            # get the value sent by the driver, available in the snapshot
            value = float(event.snapshot['Counter']['txcount']['txvalue'])
        except (IndexError, KeyError):
            continue
        # manipulate it, in this example just multiply by two
        # and transmit manipulated value back in vector rxvector
        txque.append( ('Counter', 'rxvector',  {'rxvalue':value * 2}) )


if __name__ == "__main__":

    # create queue where updated data will be transmitted
    txque = collections.deque()
    # create queue where client will put events
    rxque = collections.deque()

    # run a queclient in its own thread
    clientthread = threading.Thread(target=runqueclient, args=(txque, rxque))

    # The args argument could also have hostname and port specified
    # if the server is running elsewhere
    clientthread.start()

    print(f"Running {__file__}")

    try:

        # call blocking function
        numberdoubler(txque, rxque)

    except KeyboardInterrupt:
        # normal shutdown, dont bother displaying any output trace
        print("Shutting down")

    finally:
        # if this stops, shutdown queclient
        txque.append(None)
        # and wait for the client thread to stop
        clientthread.join()
