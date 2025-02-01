# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipydriver",
# ]
# ///

"""
Illustrates a driver receiving six files and saving them
"""

import asyncio
import indipydriver as ipd


class _GetBLOBs(ipd.IPyDriver):

    """IPyDriver is subclassed here."""

    async def rxevent(self, event):
        """On receiving data from the client, this is called
           It writes received multiple BLOBs to files"""

        if isinstance(event, ipd.newBLOBVector):
            if event.vectorname == "blobvector":
                if event.timestamp:
                    timestamp = event.timestamp.strftime('%Y%m%d_%H_%M_%S')
                else:
                    timestamp = ""
                # this vector has multiple members
                for membername, blobvalue in event.items():
                    # Each membername is of the format "member1", "member2" etc
                    filename = "blobfile" + membername[-1]
                    if timestamp:
                        filename += "_" + timestamp
                    # sizeformat is (membersize, memberformat), where memberformat is the file extension
                    membersize, memberformat = event.sizeformat[membername]
                    if memberformat:
                        filename += memberformat
                    # write blobvalue to a file with this name
                    with open(filename, "wb") as fp:
                        # Write bytes to file
                        fp.write(blobvalue)
                # send vector back to the client but with no members, this just
                # sets the state to ok to inform the client the vector has been received
                await event.vector.send_setVectorMembers(state="Ok", message=f"Saved {timestamp}")


def make_driver(devicename):
    "Creates the driver"

    # create members
    members = []
    for m in range(6):
        members.append( ipd.BLOBMember(name=f"member{m}",
                                       label=f"BLOB file {m}") )
    # set these members into a vector
    blobvector = ipd.BLOBVector( name="blobvector",
                                 label="BLOB files",
                                 group="Files",
                                 perm="wo",         # Informs client it is writing BLOBs
                                 state="Ok",
                                 blobmembers=members )
    # create a Device with this vector
    blobdevice = ipd.Device( devicename=devicename, properties=[blobvector] )

    # Create and return the Driver containing this device
    return _GetBLOBs(blobdevice)



if __name__ == "__main__":

    driver = make_driver("blobdevice")
    server = ipd.IPyServer(driver)
    print(f"Running {__file__}")
    asyncio.run(server.asyncrun())
