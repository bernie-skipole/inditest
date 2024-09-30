
"""
Requires a BLOB filepath to be provided. Attempts to send it
and waits 10 seconds then sends it again. This is to test how the client reacts
"""

import sys
sys.path.insert(0, "/home/bernie/git/indipydriver")

import asyncio
import indipydriver as ipd



class BigBlobDriver(ipd.IPyDriver):

    """IPyDriver is subclassed here to create a driver for the instrument"""


    async def hardware(self):
        """This is a continuously running coroutine which is used
           to transmit the blob to connected clients.
           This test sends the same blob continuously with ten second
           pauses."""

        blobpath = self.driverdata["blobpath"]
        # blobpath is the path to a file

        blobvector = self['bigblob']['blobvector']
        while not self.stop:
            blobvector["blobmember"] = blobpath
            # send the blob
            await blobvector.send_setVectorMembers(members=["blobmember"])
            await asyncio.sleep(10)


def make_driver(blobpath):
    "Returns an instance of the driver, blobpath is path to file"

    # create blobvector, there is no member value to set at this point
    blobmember = ipd.BLOBMember( name="blobmember",
                                 label="BigBlob")
    blobvector = ipd.BLOBVector( name="blobvector",
                                 label="BigBlob",
                                 group="File",
                                 perm="ro",
                                 state="Ok",
                                 blobmembers=[blobmember] )

    # create a device with this vector
    bigblob = ipd.Device( devicename="bigblob",
                          properties=[blobvector] )

    # Create the Driver, containing this device and
    # other objects needed to run the instrument
    driver = BigBlobDriver( bigblob,                # the device
                            blobpath=blobpath )     # path of blob to send

    # and return the driver
    return driver



if __name__ == "__main__":

    # set a file path in this call
    blobpath = ""
    while not blobpath:    
        blobpath = input("Type in a blob file path:")

    driver = make_driver(blobpath)
    server = ipd.IPyServer(driver)
    # and run the server
    print(f"Running {__file__}")
    asyncio.run( server.asyncrun() )
