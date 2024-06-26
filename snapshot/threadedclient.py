
import sys

sys.path.insert(0, "/home/bernard/git/indipyclient")

import asyncio, collections, threading, time

import indipyclient as ipc


class MyClient(ipc.IPyClient):

    async def rxevent(self, event):
        "Gets the value as it is received and create a snapshot"

        if isinstance(event, ipc.setNumberVector):
            if event.devicename != "Counter":
                return
            if event.vectorname != "txcount":
                return
            # create snapshot
            snap = self.snapshot()
            # snap is a copy of devices and vectors
            # put this snapshot into dque, to be read by a function
            # running in a thread
            self.clientdata['snapque'].append(snap)



# a blocking function to be run in a thread

def numberdoubler(myclient, snapque):
    """get item from snapque, manipulate it, and send a value
       back to the driver.
       as a test, make this blocking and run it in a thread"""
    while True:
        try:
            snap = snapque.popleft()
        except IndexError:
            time.sleep(0.1)
            continue
        # get the value sent by the driver
        value = float(snap['Counter']['txcount']['txvalue'])
        # manipulate it, in this example just multiply by two
        # and transmit manipulated value back
        myclient.send_newVector('Counter', 'rxvector',  members={'rxvalue':value * 2})



if __name__ == "__main__":

    # create queue where client will put snapshots
    snapque = collections.deque()
    # create a myclient object
    myclient = MyClient(snapque = snapque)

    # run numberdoubler in its own thread
    clientapp = threading.Thread(target=numberdoubler, args=(myclient, snapque),)
    clientapp.start()

    # run myclient.asyncrun()
    asyncio.run(myclient.asyncrun())
