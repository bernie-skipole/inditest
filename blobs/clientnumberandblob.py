# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipyclient >= 0.9.3"
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

# Enable xml logging to stdout

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)



class MyClient(ipc.IPyClient):

    async def rxevent(self, event):
        "Handle define defBLOBVector, and display received numbers and switch values"

        if isinstance(event, ipc.defBLOBVector):
            if event.devicename == 'blobgetter' and event.vectorname == 'blobvector':
                await self.send_enableBLOB("Only", 'blobgetter', 'blobvector')
            else:
                # any other BLOBs, send the appropriate enableBLOB instruction
                # doing this since we have set resend_enableBLOB_on_def to be False
                await self.resend_enableBLOB(event.devicename, event.vectorname)
            return

        if event.devicename != 'blobgetter':
            # Any other device is not handled here
            pass
        elif isinstance(event, ipc.setNumberVector):
            if event.vectorname == 'countvector' and "count" in event:
                try:
                    value = int( ipc.getfloat(event["count"]) )
                except:
                    print("Invalid number received")
                else:
                    print( f"Received {value}" )
        elif isinstance(event, ipc.setSwitchVector):
            if event.vectorname == 'getfileswitch' and "getfilenow" in event:
                print(f"Switch Received : {event['getfilenow']}")
        elif isinstance(event, ipc.setBLOBVector):
            # Do not show the full BLOB, just indicate it is received
            if event.vectorname == 'blobvector' and "blobmember" in event:
                try:
                    size, fmt = event.sizeformat['blobmember']
                except:
                    print("Invalid BLOB received")
                else:
                    print(f"BLOB received, size: {size} extension: {fmt}")


    async def hardware(self):
        "create a switch On event every ten seconds to request the blob file, to show it in action"
        while True:
            await asyncio.sleep(10)
            await self.send_newVector('blobgetter', 'getfileswitch', members={'getfilenow':'On'})


myclient = MyClient()
# do not auto resend_enableBLOB, we are doing that in the above code
myclient.resend_enableBLOB_on_def = False
# set verbosity to 2, to avoid listing full BLOBs in the xml
myclient.debug_verbosity(2)

asyncio.run(myclient.asyncrun())
