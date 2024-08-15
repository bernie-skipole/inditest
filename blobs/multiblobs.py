
"""
Illustrates a driver receiving six files and saving them
"""

import asyncio
import indipydriver as ipd


class GetBLOBs(ipd.IPyDriver):

    """IPyDriver is subclassed here."""

    async def rxevent(self, event):
        """On receiving data from the client, this is called
           It writes received multiple BLOBs to files"""

        match event:

            case ipd.getProperties():
                await event.vector.send_defVector()

            case ipd.newBLOBVector(devicename="blobdevice",
                                   vectorname="blobvector"):
                # this vector has multiple members
                for membername, blobvalue in event.items():
                    # Each membername is of the format "member1", "member2" etc
                    filename = "blobfile" + membername[-1]
                    # sizeformat is (membersize, memberformat), where memberformat is the file extension
                    sizeformat = event.sizeformat[membername]
                    if sizeformat[1]:
                        filename += sizeformat[1]
                    # write blobvalue to a file with this name
                    with open(filename, "wb") as fp:
                        # Write bytes to file
                        fp.write(blobvalue)
                # send vector back to the client but with no members, this just
                # sets the state to ok to inform the client the vector has been received
                await event.vector.send_setVectorMembers(state="Ok")


def make_driver():
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
    blobdevice = ipd.Device( devicename="blobdevice", properties=[blobvector])

    # Create and return the Driver containing this device
    return GetBLOBs(blobdevice)



if __name__ == "__main__":

    driver = make_driver()
    server = ipd.IPyServer(driver)
    asyncio.run(server.asyncrun())
