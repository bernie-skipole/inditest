# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipyclient >= 0.9.3"",
# ]
# ///


"""Connects to the driver of servenumberandblob.py and prints
   the received count number

   Sends an enable blob instruction of 'Only' to the blob vector

   sends a switch instruction to get the blob

   Logs xml to console so it can be viewed.
"""

import asyncio, logging, sys
import indipyclient as ipc

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)



class MyClient(ipc.IPyClient):

    async def rxevent(self, event):
        if isinstance(event, ipc.defBLOBVector):
            if event.devicename == 'blobgetter' and event.vectorname == 'blobvector':
                await self.send_enableBLOB("Only", 'blobgetter', 'blobvector')
            else:
                await self.resend_enableBLOB(event.devicename, event.vectorname)

        elif isinstance(event, ipc.setNumberVector):
            if event.devicename == 'blobgetter' and event.vectorname == 'countvector' and "count" in event.vector:
                print( ipc.getfloat(event.vector["count"]) )

       # do not bother with events for receiving switch and blobs - they will be shown in the debug logs

    async def hardware(self):
        "create a switch On event every ten seconds to request the blob file, just to show it in action"
        while True:
            await asyncio.sleep(10)
            await self.send_newVector('blobgetter', 'getfileswitch', members={'getfilenow':'On'})


myclient = MyClient()
# do not auto resend_enableBLOB, we are dealing with that
myclient.resend_enableBLOB_on_def = False
myclient.debug_verbosity(2)

asyncio.run(myclient.asyncrun())
