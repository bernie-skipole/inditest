# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipyclient",
# ]
# ///

#import sys
#sys.path.insert(0, "/home/bernard/git/indipyclient")

import asyncio

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
            snap = event.vector.snapshot()
            # snap is a copy of this vector
            # print a jsondump
            print(snap.dumps(indent=2))


if __name__ == "__main__":

    # create a myclient object
    myclient = MyClient()
    print(f"Running {__file__}")
    # run myclient.asyncrun()
    asyncio.run(myclient.asyncrun())
