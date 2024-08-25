# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipyclient",
#     "indipydriver",
# ]
# ///

"""
Illustrates a driver receiving a file and saving it
"""

import asyncio
import indipydriver as ipd


class GetBLOBDriver(ipd.IPyDriver):

    """IPyDriver is subclassed here."""

    async def rxevent(self, event):
        """On receiving data from the client, this is called
           It writes received BLOB data to file blobfile"""

        match event:

            # event.vector is the vector being requested or altered
            # event[membername] is the new value

            case ipd.getProperties():
                await event.vector.send_defVector()

            case ipd.newBLOBVector(devicename="getblob",
                                   vectorname="getvector") if 'getmember' in event:
                # a new value has been received from the client
                blobvalue = event["getmember"]
                # sizeformat is (membersize, memberformat)
                sizeformat = event.sizeformat["getmember"]
                if sizeformat[1]:
                    filename = "blobfile" + sizeformat[1]
                else:
                    filename = "blobfile"
                # write this to a file
                with open(filename, "wb") as fp:
                    # Write bytes to file
                    fp.write(blobvalue)
                # send vector back to the client but with no members, this just
                # sets the state to ok to inform the client it has been received
                await event.vector.send_setVectorMembers(state="Ok")


def make_driver():
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
    getblob = ipd.Device( devicename="getblob", properties=[getvector])

    # Create the Driver containing this device
    driver = GetBLOBDriver(getblob)

    # and return the driver
    return driver


if __name__ == "__main__":

    driver = make_driver()
    server = ipd.IPyServer(driver)
    print(f"Running {__file__}")
    asyncio.run(server.asyncrun())
