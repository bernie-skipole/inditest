
"""
Illustrates a driver receiving a file and saving it
"""

# ignore these lines, used for my own testing
#import sys
#sys.path.insert(0, "/home/bernard/git/indipydriver")

import asyncio
import indipydriver as ipd


class _GetBLOBDriver(ipd.IPyDriver):

    """IPyDriver is subclassed here."""

    async def rxevent(self, event):
        """On receiving data from the client, this is called
           It writes received BLOB data to a file"""

        # event.vector is the vector being requested or altered
        # event[membername] is the new value

        if isinstance( event, ipd.newBLOBVector ):
            if event.vectorname == "getvector" and 'getmember' in event:
                # a new BLOB has been received from the client
                blobvalue = event["getmember"]
                # sizeformat is (membersize, memberformat)
                membersize, memberformat = event.sizeformat["getmember"]
                # make filename from timestamp
                if event.timestamp:
                    filename = "blobfile_" + event.timestamp.strftime('%Y%m%d_%H_%M_%S')
                else:
                    filename = "blobfile"
                if memberformat:
                    filename = filename + memberformat
                # write this to a file
                with open(filename, "wb") as fp:
                    # Write bytes to file
                    fp.write(blobvalue)
                # send vector back to the client but with no members, this just
                # sets the state to ok to inform the client it has been received
                await event.vector.send_setVectorMembers(state="Ok", message=f"Saved as {filename}")


def make_driver(devicename):
    "Creates the driver"

    # create member
    getmember = ipd.BLOBMember( name="getmember",
                                label="BLOB file" )
    # set this member into a vector
    getvector = ipd.BLOBVector( name="getvector",
                                label="BLOB",
                                group="File",
                                perm="wo",         # Informs client it is writing a BLOB
                                state="Ok",
                                blobmembers=[getmember] )
    # create a Device with this vector
    getblob = ipd.Device( devicename=devicename, properties=[getvector])

    # Create the Driver containing this device
    driver = _GetBLOBDriver(getblob)

    # and return the driver
    return driver


if __name__ == "__main__":

    driver = make_driver("getblob")
    server = ipd.IPyServer(driver)
    print(f"Running {__file__}")
    asyncio.run(server.asyncrun())
