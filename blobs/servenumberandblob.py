# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "indipydriver>=3.1.1",
#     "indipyserver>=0.0.3"
# ]
# ///


"""
Serves an incrementing number and a file whenever a switch On is submitted

This example was created, together with clientnumberandblob.py, to test the
scenario where a client sets enable blob to Only on a property, and to ensure
that other properties (the changing numbers) are unaffected.
"""

import asyncio

import indipydriver as ipd

import indipyserver as ips


class _Driver(ipd.IPyDriver):

    """IPyDriver is subclassed here."""

    async def rxevent(self, event):
        """On receiving a switch from the client, this is called
           It sends the source file of this code as the BLOB"""

        if isinstance( event, ipd.newSwitchVector ):
            if event.vectorname == "getfileswitch" and 'getfilenow' in event:
                if event['getfilenow'] == "On":
                    # return the switch On value
                    event.vector['getfilenow'] = 'On'
                    await event.vector.send_setVector(state='Ok')
                    # send the file, so first obtain the blobvector
                    blobvector = self['blobgetter']['blobvector']
                    blobvector["blobmember"] = __file__
                    # send the blob
                    await blobvector.send_setVectorMembers(members=["blobmember"])
                    # set the switch to Off again
                    await asyncio.sleep(0.2)
                    event.vector['getfilenow'] = 'Off'
                    await event.vector.send_setVector(state='Idle')
                else:
                    # so switch is Off, accept it, but do not send a blob
                    event.vector['getfilenow'] = 'Off'
                    await event.vector.send_setVector(state='Ok')
                    # after the acknowledgement, set the state back to idle
                    await asyncio.sleep(0.5)
                    await event.vector.send_setVector(state='Idle')
                   

    async def hardware(self):
        """Sends a counting number vector"""

        countvector = self['blobgetter']['countvector']
        while not self.stop:
            # send an incrementing count every second
            await asyncio.sleep(1)
            currentvalue = countvector["count"]
            countvector["count"] = int(currentvalue) + 1
            # and send the new vector
            await countvector.send_setVector()
    

def make_driver():
    "Creates the driver"

    # number counter
    count = ipd.NumberMember( name = "count",
                              label = "Counter",
                              format = "%d",
                              membervalue = 0 )
    countvector = ipd.NumberVector( name="countvector",
                                    label="Counter",
                                    group="File",
                                    state="Ok",
                                    perm="ro",
                                    numbermembers=[count] )

    # create switch
    getfilenow = ipd.SwitchMember( name='getfilenow',
                                  label="Get File",
                                  membervalue='Off' )
    getfileswitch = ipd.SwitchVector( name = 'getfileswitch',
                                   label = "File Getter",
                                   group = 'File',
                                   perm = "wo",
                                   state = "Idle",
                                   rule = "AtMostOne",
                                   switchmembers = [getfilenow])

    # create blob
    blobmember = ipd.BLOBMember( name="blobmember",
                                label="BLOB file" )
    # set this member into a vector
    blobvector = ipd.BLOBVector( name="blobvector",
                                label="BLOB",
                                group="File",
                                perm="ro",         # Informs client it is reading a BLOB
                                state="Idle",
                                blobmembers=[blobmember] )

    # create a Device with these vectors
    getblob = ipd.Device( devicename="blobgetter", properties=[countvector, getfileswitch, blobvector])

    # Create the Driver containing this device
    driver = _Driver(getblob)

    # and return the driver
    return driver


if __name__ == "__main__":

    driver = make_driver()
    server = ips.IPyServer(driver)
    print(f"Running {__file__} with indipydriver {ipd.version} and indipyserver {ips.version}")
    asyncio.run(server.asyncrun())
